const platforms = document.getElementsByName('platform-select');
const forms = document.querySelectorAll('form');
const app_name_info = document.getElementsByName('app-name-info')[0];
const app_svn_info = document.getElementsByName('svn-info')[0];
const app_template_info = document.getElementsByName('template-info')[0];
const app_info_card = document.getElementById('app-info-card');
const base_url = get_base_url();

initialize();
var app_info = {};

platforms.forEach(selectPid => {
    selectPid.addEventListener('change', function() {
        platform_id = selectPid.value;
        selectApp = selectPid.form[1];

        initAppList(selectApp)
        if (platform_id == -1) {
            return;
        }
        get_apps(platform_id)
        .then(handle_response_status)
        .then(response => response.json())
        .then(function (data) {
            const sortedKeys = sortAppList(data);
            sortedKeys.forEach(function (key) {
                let newNode = document.createElement('option');
                newNode.value = key;
                newNode.textContent = data[key];
                selectApp.appendChild(newNode);
            }); 
        })
        .catch(error => {
            generateModalContent('error', error)
        });
    })
})

forms.forEach(form => {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        form_type = form.id.split('-')[0];

        var formData = new FormData(form);
        if(!formData.get('platform-select')) {
            generateModalContent("alert", "請選擇平台!!")
            return false;
        }

        data = {}
        var platform_id = formData.get('platform-select');
        data['platform_id'] = platform_id

        if (form_type == 'new') {
            let svn_file = (formData.get('app-url')).trim().replace('https://', 'http://');
            let n = svn_file.lastIndexOf('/') + 1;
            let template = svn_file.substring(n);
            svn_file = svn_file.substring(0, n);
            let app_name = (formData.get('app-name')).trim();

            template_error = check_templates(platform_id, template)
            if(template_error == true) {
                generateModalContent("alert", "template格式錯誤!!")
                return false;
            }

            data['app_name'] = app_name
            data['svn_file'] = svn_file
            data['template'] = template

            insert_app(platform_id, data, '新增');
        }
        else if (form_type == 'modify') {
            if(!formData.get('app-select')) {
                generateModalContent("alert", "請選擇App!!")
                return false;
            }
            let app_id = formData.get('app-select');
            
            get_app_info(platform_id, app_id);
        }
        else {
            data['app_id'] = app_info['app_id'];
            data['app_name'] = app_name_info.value.trim();
            svn_file = app_svn_info.value.trim().replace('https://', 'http://');
            data['svn_file'] = svn_file.slice(-1) !== '/' ? svn_file += '/' : svn_file;
            data['template'] = app_template_info.value.trim();
            
            let diff_checker = compareDictValues(data);
            if (diff_checker) {
                generateModalContent('alert', 'App無更改')
                return false;
            }
            update_app_info(data);
        }

    })
})

function check_templates(platform_id, template) {
    
    let error = false;
    switch (platform_id) {
        case '1':
            if (template !== 'lang-en-US.js' && template !== 'en-US.js') {
                error = true;
            }
            break;
        case '4':
            if (template !== 'strings.xml') {
                error = true;
            }
            break;
        case '3':
        case '5':
            if (template !== 'Localizable.strings' && template !== 'InfoPlist.strings') {
                error = true;
            }
            break;
    }

    return error;
}

function insert_app(platform_id, data, type) {
    checker = get_apps(platform_id);
    checker
    .then(handle_response_status)
    .then(response => response.json())
    .then(res => {
        if(Object.values(res).includes(data['app_name']) == true) {
            generateModalContent("alert", "App名稱已存在!!")
            return false;
        }

        fetch(`/${base_url}/app`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(function (data) {
            msgHandler(data, type);
        })
    })
    .catch(error => {
        generateModalContent('error', error)
    })
}

function msgHandler(data, type) {
    if(data['msg'] === 'success') {
        console.log(data['test_mode'])
        console.log(data['test_mode'] == true)
        if(data['test_mode'] == true) {
            generateModalContent("alert", data['test_msg'])
        } else {
            generateModalContent("alert", type + "App成功!!")
        }
        initialize();
    }
    else if(data['msg'] === 'svn_file + template duplicate') {
        generateModalContent("alert", 'SVN路徑重複!' + '\napp名稱: ' + data['app_name'])
    }
    else if(data['msg'] === 'No file') {
        generateModalContent("alert", "找不到SVN路徑下的template文件!!")
    }
    else if(data['msg'] === 'Cannot connect to svn') {
        generateModalContent("alert", "無法連線至SVN\n請確認SVN路徑正確或是SVN!!")
    }
    else if(data['msg'] === 'User not found') {
        generateModalContent("alert", "您沒有權限新增或修改App，請向管理員確認權限!!")
    }
    else if(data['msg'] === 'svn path error') {
        generateModalContent("alert", "svn路徑錯誤!!")
    }
    else {
        generateModalContent("alert", type + "App失敗!!")
    }
}

function get_app_info(platform_id, app_id) {
    fetch(`/${base_url}/app/${app_id}`, {
        method: 'GET',
    })
    .then(handle_response_status)
    .then(response => response.json())
    .then(function(data) {
        platforms[2].value = platform_id;
        app_name_info.value = data['app_name'];
        app_svn_info.value = data['svn_file'] || '無svn路徑，請補上';
        app_template_info.value = data['template'] || '無template，請補上';
        app_info = {
            'platform_id': platform_id,
            'app_id': data['app_id'],
            'app_name': data['app_name'],
            'svn_file': data['svn_file'],
            'template': data['template'],
        }

        app_info_card.style.display = 'block';
    })
    .catch(error => {
        generateModalContent('error', error)
    })
}

function compareDictValues(data) {
    const keys = Object.keys(app_info);

    for (let key of keys) {
        if (app_info[key] !== data[key]) {
            return false;
        }
    }
    return true;
}

function update_app_info(app_info) {
    checker = get_apps(app_info['platform_id']);
    checker
    .then(handle_response_status)
    .then(response => response.json())
    .then(data => {
        if(Object.values(data).includes(app_info['app_name']) == true && data[app_info['app_id']] !== app_info['app_name']) {
            generateModalContent("alert", "App名稱已存在!!")
            return false;
        }

        svn_path_exist_template = check_svn_path(app_info['platform_id'], app_info['svn_file']);
        if(svn_path_exist_template !== true) {
            generateModalContent("alert", "SVN_路徑請不要包含template!!")
            return false;
        }

        template_error = check_templates(app_info['platform_id'], app_info['template'])
        if(template_error == true) {
            generateModalContent("alert", "template格式錯誤!!")
            return false;
        }

        fetch(`/${base_url}/app/${app_info['app_id']}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(app_info)
        })
        .then(response => response.json())
        .then(function (data) {
            msgHandler(data, '修改');
        })
    })
    .catch(error => {
        generateModalContent('error', error)
    })
}

function check_svn_path(platform_id, svn_file) {
    if (platform_id == '1') {
        if (svn_file.indexOf("en-US.js") !== -1 || svn_file.indexOf("lang-en-US.js") !== -1) {
            return false;
        }
    }
    else if (platform_id == '4'){
        if (svn_file.indexOf("strings.xml") !== -1) {
            return false;
        }
    }
    else if (platform_id == '5'){
        if (svn_file.indexOf("Localizable.strings") !== -1) {
            return false;
        }
    }
    return true;
}

function initialize() {
    forms.forEach(form => {
        form.reset()
    })
}