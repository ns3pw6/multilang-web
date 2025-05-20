from server import db, logger
from flask import jsonify, session, Response, send_file
from utility.file_utils import generate_excel, archive_files, cleanup_files
from model.dbModel import ProofreadProject, ProofreadLog, ProofreadString, Action_Type
from model.log import Log
from model.user import User
from sqlalchemy import desc
from typing import Dict

class ProofreadService():
    
    def __init__(self) -> None:
        pass
        
    def __build_log(self, type_name: str, data: Dict) -> None:
        """Construct and save a log entry for a specific action type and associated data."""
        type_id = Action_Type.query.filter_by(type_name=type_name).first().type_id
        log_string = f"Proofread project <br>project_name: {data['project_name']} <br> spec_link: {data['spec_link']}"
        log = Log(
            u_id=data['user_id'],
            type_id=type_id,
            log=log_string
        )
        db.session.add(log)    
    
    def __handle_test_mode(self, action: str, data: Dict) -> Response:
        """Handle test mode by logging the action and returning a success message."""
        preview = f'測試模式預覽{action}資訊如下:<br>'
        for key, value in data.items():
            preview += f'{key}: {value} <br>'

        return jsonify({
            'msg': f'{preview}',
            'test_mode': True,
        }), 200
    
    def get_projects(self, data: Dict) -> tuple[Dict, int, int]:
        """
        Retrieve projects based on filters and pagination.

        Args:
            data (dict): Request data containing search criteria and pagination info.
                Expected keys: 'search_type', 'content', 'page', 'per_page'.

        Returns:
            tuple: A dictionary of project data, the total project count, and the HTTP status code.
        """
        filters = []
        search_type = data.get('search_type')
        content = data.get('content')
        
        if search_type and content:
            if search_type == 'proj_name':
                filters.append(ProofreadProject.project_name.ilike(f'%{content}%'))
            elif search_type == 'proj_id':
                filters.append(ProofreadProject.project_id==content)
            elif search_type == 'maintainer':
                user_id = User.get_user_id(content)
                if not user_id:
                    return {}, 0, 200
                filters.append(ProofreadProject.person_in_charge==user_id)
            elif search_type == 'reviewer':
                user_id = User.get_user_id(content)
                if not user_id:
                    return {}, 0, 200
                filters.append(ProofreadProject.reviewer==user_id)
        filters.append(ProofreadProject.deleted==0)
        
        page = data.get('page', 1)
        per_page = data.get('per_page', 15)
        offset = (page - 1) * per_page
        
        query = ProofreadProject.query.filter(*filters) \
                                      .order_by(desc(ProofreadProject.project_id)) \
                                      .limit(per_page) \
                                      .offset(offset) \
                                      .all()
                                      
        total_projects = ProofreadProject.query.filter(*filters).count()
                                      
        project_data = {
            project.project_id: {
                'project_name': project.project_name,
                'person_in_charge': project.person_in_charge_user.name,
                'reviewer': project.reviewer_user.name if project.reviewer_user else None,
            }
            for project in query
        }
        
        return project_data, total_projects, 200
    
    def get_project_by_id(self, project_id: int) -> tuple[Dict, int]:
        """
        Retrieve project details by project ID.

        Args:
            project_id (int): The ID of the project to retrieve.

        Returns:
            tuple: A dictionary containing project details and the HTTP status code.
        """
        try:
            query = ProofreadProject.query.filter_by(project_id=project_id).first()
            if not query:
                return jsonify({'msg': 'Not Found'}), 404
            
            query_strings = ProofreadString.query.filter_by(project_id=project_id,deleted=0).all()
            strings = [(string.ps_id, string.string) for string in query_strings]
            
            project_data = {
                'project_name': query.project_name,
                'spec_link': query.spec_link,
                'strings': strings,
            }

            return project_data, 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error occurred during get proofread project details: {str(e)}", exc_info=True)
            return jsonify({'msg': str(e)}), 500
    
    def new_project(self, data: Dict) -> Response:
        """
        Create a new proofread project.

        Args:
            data (dict): The project details including 'project_name' and 'spec_link'.

        Returns:
            tuple: A dictionary with a success message or error details, and the HTTP status code.
        """
        try:
            user_id = User.get_user_id(session.get('username'))

            project_name = data['project_name'].strip()
            spec_link = data['spec_link'].strip()

            new_project = ProofreadProject(
                project_name=project_name,
                spec_link=spec_link,
                person_in_charge=user_id
            )
            
            test_mode = session.get('test_mode')
            if test_mode:
                return self.__handle_test_mode("新增", data)
            
            data['user_id'] = user_id
            self.__build_log('New', data)
            
            db.session.add(new_project)
            db.session.commit()
            return jsonify({
                'msg': '新增成功!',
                'test_mode': False
            }), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error occurred during proofread project insertion: {str(e)}", exc_info=True)
            return jsonify({'msg': str(e)}), 500

    def update_project_info(self, data: Dict) -> Response:
        """
        Update project information including name and specification link.

        Args:
            data (Dict): Dictionary containing project update details
                Required keys: 'project_id', 'project_name', 'spec_link'

        Returns:
            tuple: Response message dictionary and HTTP status code
        """
        try:
            project_id = data['project_id']
            project_name = data['project_name'].strip()
            spec_link = data['spec_link'].strip()
            update_flag = False

            user_id = User.get_user_id(session.get('username'))
            project = ProofreadProject.query.filter_by(project_id=project_id).first()
            if not project:
                return jsonify({'msg': 'project not found'}), 404
            
            test_mode = session.get('test_mode')
            if test_mode:
                return self.__handle_test_mode("更新", data)
            
            log_string = f'Proofread project_id: {project_id}'
            old_project_name = project.project_name
            old_spec_link = project.spec_link
            if old_project_name != project_name:
                project.project_name = project_name
                update_flag = True
                log_string += f'<br>old_project_name: {old_project_name}<br> project_name: {project_name}'
            if old_spec_link != spec_link:
                project.spec_link = spec_link
                update_flag = True
                log_string += f'<br>old_spec_link: {old_spec_link}<br> spec_link: {spec_link}'
            
            if update_flag:
                type_id = Action_Type.query.filter_by(type_name='Update').first().type_id
                log = Log(
                    u_id=user_id,
                    type_id=type_id,
                    log=log_string
                )
                db.session.add(log)
                db.session.commit()
                return jsonify({
                    'msg': '更新成功!',
                    'test_mode': False
                }), 200
            else:
                return jsonify({'msg': '無更新資料!'}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error occurred during proofread project updating: {str(e)}", exc_info=True)
            return jsonify({'msg': str(e)}), 500

    def delete_project(self, project_id: int) -> Response:
        """
        Mark a project as deleted in the database.

        Args:
            project_id: ID of the project to delete

        Returns:
            tuple: Response message dictionary and HTTP status code
        """
        try:
            query = ProofreadProject.query.filter_by(project_id=project_id).first()
            if not query:
                return jsonify({'msg': 'Not Found'}), 404
            
            test_mode = session.get('test_mode')
            if test_mode:
                datas = {
                    'project_id': query.project_id,
                    'project_name': query.project_name,
                    'spec_link': query.spec_link
                }
                return self.__handle_test_mode("刪除", datas)
            
            user_id = User.get_user_id(session.get('username'))
            type_id = Action_Type.query.filter_by(type_name='Remove').first().type_id
            log = Log(
                u_id=user_id,
                type_id=type_id,
                log=f'Proofread project <br>project_id: {query.project_id} <br>project_name: {query.project_name}'
            )
            
            query.deleted = 1
            db.session.add(log)
            db.session.commit()
            return jsonify({
                'msg': '刪除成功!',
                'test_mode': False            
            }), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error occurred during proofread project removing: {str(e)}", exc_info=True)
            return jsonify({'msg': str(e)}), 500

    def insert_project_string(self, data: Dict) -> Response:
        """
        Add a new string to an existing project.

        Args:
            data (Dict): Dictionary containing string details
                Required keys: 'project_id', 'string'

        Returns:
            tuple: Response message dictionary and HTTP status code
        """
        try:
            project_id = data.get('project_id')
            string = data.get('string', None).strip()
            
            test_mode = session.get('test_mode')
            if test_mode:
                return self.__handle_test_mode("新增字串", data)
            
            new_string = ProofreadString(
                project_id=project_id,
                string=string
            )
            db.session.add(new_string)
            db.session.flush()
            
            user_id = User.get_user_id(session.get('username'))
            type_id = Action_Type.query.filter_by(type_name='Create').first().type_id
            log = ProofreadLog(
                u_id=user_id,
                action=type_id,
                ps_id=new_string.ps_id,
                new_string=string
            )
            
            db.session.add(log)
            db.session.commit()
            return jsonify({
                'msg': '新增字串成功!',
                'test_mode': test_mode
            }), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error occurred during proofread project string inserting: {str(e)}", exc_info=True)
            return jsonify({'msg': str(e)}), 500
        
    def update_project_string(self, data: Dict) -> Response:
        """
        Update an existing string in a project.

        Args:
            data (Dict): Dictionary containing string update details
                Required keys: 'ps_id', 'string'

        Returns:
            tuple: Response message dictionary and HTTP status code
        """
        try:
            user_id = User.get_user_id(session.get('username'))
            ps_id = data.get('ps_id')
            string = data.get('string', None).strip()
            
            query = ProofreadString.query.filter_by(ps_id=ps_id).first()
            if not query:
                return jsonify({'msg': 'Not Found!'}), 404
            
            test_mode = session.get('test_mode')
            if test_mode:
                datas = {
                    'ps_id': query.ps_id,
                    'string': query.string
                }
                return self.__handle_test_mode("更新字串", datas)
            
            old_string = query.string
            query.string = string
            type_id = Action_Type.query.filter_by(type_name='Update').first().type_id
            log = ProofreadLog(
                u_id=user_id,
                action=type_id,
                ps_id=query.ps_id,
                old_string=old_string,
                new_string=string
            )
            
            db.session.add(log)
            db.session.commit()
            return jsonify({
                'msg': '更新字串成功!',
                'test_mode': test_mode   
            }), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error occurred during proofread project string updating: {str(e)}", exc_info=True)
            return jsonify({'msg': str(e)}), 500
    
    def remove_project_string(self, ps_id: int) -> Response:
        """
        Mark a project string as deleted.

        Args:
            ps_id: ID of the project string to remove

        Returns:
            tuple: Response message dictionary and HTTP status code
        """
        try:
            user_id = User.get_user_id(session.get('username'))
            
            string = ProofreadString.query.filter_by(ps_id=ps_id).first()
            if not string:
                return jsonify({'msg': 'Not Found'}), 404
            
            test_mode = session.get('test_mode')
            if test_mode:
                datas = {
                    'ps_id': string.ps_id,
                    'string': string.string
                }
                return self.__handle_test_mode("刪除字串", datas)
            
            string.deleted = 1
            
            type_id = Action_Type.query.filter_by(type_name='Remove').first().type_id
            log = ProofreadLog(
                u_id=user_id,
                action=type_id,
                ps_id=ps_id,
                old_string=string.string
            )
            
            db.session.add(log)
            db.session.commit()
            return jsonify({'msg': '刪除字串成功!'}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error occurred during proofread project string removing: {str(e)}", exc_info=True)
            return jsonify({'msg': str(e)}), 500

    def project_update_log(self, project_id: int) -> Response:
        """
        Retrieve the update history log for a project.

        Args:
            project_id: ID of the project to get logs for

        Returns:
            tuple: Dictionary containing log entries and HTTP status code
        """
        try:
            strings = ProofreadString.query.filter_by(project_id=project_id).all()
            ps_ids = [ps.ps_id for ps in strings]
            proofread_logs = ProofreadLog.query.filter(ProofreadLog.ps_id.in_(ps_ids)) \
                                               .order_by(desc(ProofreadLog.log_id)) \
                                               .all()
            if not proofread_logs:
                return jsonify({'msg': 'Not Found'}), 404
            
            logs = {
                log.log_id: {
                    'username': log.person_recorded.name,
                    'type': log.log_type.type_name,
                    'old_string': log.old_string,
                    'new_string': log.new_string,
                    'time': log.time.strftime('%Y/%m/%d'),
                }
                for log in proofread_logs
            }
            
            return jsonify(logs), 200
        except Exception as e:
            logger.error(f"Error occurred during fetching proofread project log: {str(e)}", exc_info=True)
            return jsonify({'msg': str(e)}), 500
    
    def update_person_in_charge(self, project_id: int) -> Response:
        """
        Update the person in charge for a project.

        Args:
            project_id: ID of the project to update

        Returns:
            tuple: Response message dictionary and HTTP status code
        """
        try:
            username = session.get('username')
            user_id = User.get_user_id(username)
            
            project = ProofreadProject.query.filter_by(project_id=project_id).first()
            
            test_mode = session.get('test_mode')
            if test_mode:
                datas = {
                    'project_id': project.project_id,
                    'project_name': project.project_name,
                    'spec_link': project.spec_link,
                    'origin_maintainer': project.person_in_charge_user.name,
                    'change_maintainer': username
                }
                return self.__handle_test_mode("更新負責人", datas)
            
            project.person_in_charge = user_id
            db.session.commit()

            return jsonify({
                'msg': f'負責人已更新成: {session['username']}',
                'test_mode': False
            }), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error occurred during updating proofread project maintainer: {str(e)}", exc_info=True)
            return jsonify({'msg': str(e)}), 500
    
    def proofread_finished(self, project_id: int) -> Response:
        """
        Mark a project as completed by setting the reviewer.

        Args:
            project_id: ID of the project to mark as finished

        Returns:
            tuple: Response message dictionary and HTTP status code
        """
        try:
            username = session.get('username')
            user_id = User.get_user_id(username)
            
            project = ProofreadProject.query.filter_by(project_id=project_id).first()
            
            test_mode = session.get('test_mode')
            if test_mode:
                datas = {
                    'project_id': project.project_id,
                    'project_name': project.project_name,
                    'spec_link': project.spec_link,
                    'origin_reviewer': project.reviewer_user.name if project.reviewer_user else None,
                    'change_reviewer': username
                }
                return self.__handle_test_mode("校閱完成", datas)
            
            project.reviewer = user_id
            db.session.commit()
            
            return jsonify({'msg': f'已完成校閱!'}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error occurred during updating proofread project reviewer: {str(e)}", exc_info=True)
            return jsonify({'msg': str(e)}), 500

    def download(self, proofread_id, strings):
        """Downlaod proofread strings"""
        try:
            if not strings:
                return jsonify({'msg': 'No strings to download'}), 404
            response, msg, unique_dir = generate_excel(strings, 'dpr')
            if not response:
                return jsonify({'msg': msg}), 500
            
            zip_file_path = archive_files(unique_dir, 'excel')
            return send_file(zip_file_path, as_attachment=True)
        except Exception as e:
            logger.error(f"Unexpected error when download proofread_id ({proofread_id}) excel: {e}", exc_info=True)
            return jsonify({'msg': str(e)}), 500
        finally:
            if strings:
                last_slash_index = zip_file_path.rfind('/')
                zip_file_path = zip_file_path[:last_slash_index]
                cleanup_files(unique_dir)
                cleanup_files(zip_file_path)
