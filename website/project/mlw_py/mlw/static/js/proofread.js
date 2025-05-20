const forms = document.querySelectorAll('form');
const tableBody = document.querySelectorAll('tbody')[0];
const newProjectBtn = document.getElementById('newProjectBtn');
const editBtns = document.getElementsByClassName('edit-btn');
const cancelBtns = document.getElementsByClassName('cancel-btn');
const base_url = get_base_url();

let currentPage = 1;
const itemsPerPage = 15;
const url = `http://${window.location.host}/${base_url}/proofread`;
let log_data;

initialize()

function initialize() {
    forms.forEach(form => {
        form.reset()
    })
}

forms.forEach(form => {
    form.addEventListener('submit', function(e) {
        e.preventDefault()
        form_type = form.id.split('-')[0];
        var formData = new FormData(form);

        if (form_type == 'proofread') {
            search_proj(formData);
        }
        else if (form_type == 'project') {
            formData.get('project-name');
            formData.get('spec-link');
            update_project(formData);
        }
        else if (form_type == 'insert') {
            formData.get('content');
            content = formData.get('content').trim()
            if (!content) {
                generateModalContent('alert', '請輸入字串!');
                return false;
            }
            insert_string(formData);
        }
    })
})

Array.from(editBtns).forEach(editBtn => {
    editBtn.addEventListener('click', e => {
        const btn_td = editBtn.closest('td'); // 找到包含按鈕的 <td> 元素
        const text_td = btn_td.previousElementSibling;
        const span = text_td.querySelector('span'); // 找到 <span> 元素
        const textarea = text_td.querySelector('textarea'); // 找到 <textarea> 元素
        const saveButton = btn_td.querySelector('.save-btn'); // 找到 儲存 按鈕
        const cancelButton = btn_td.querySelector('.cancel-btn'); // 找到 取消 按鈕
        const editButton = btn_td.querySelector('.edit-btn'); // 找到 編輯 按鈕
        const removeButton = btn_td.querySelector('.remove-btn'); // 找到 刪除 按鈕

        // 隱藏 <span>、編輯和刪除按鈕
        span.style.display = 'none';
        editButton.style.display = 'none';
        removeButton.style.display = 'none';

        // 顯示 <textarea>、儲存和取消按鈕
        textarea.style.display = 'block';
        textarea.classList.add('form-control');
        saveButton.style.display = 'inline-block';
        cancelButton.style.display = 'inline-block';
    })
})

Array.from(cancelBtns).forEach(cancelBtn => {
    cancelBtn.addEventListener('click', e => {
        const btn_td = cancelBtn.closest('td'); // 找到包含按鈕的 <td> 元素
        const text_td = btn_td.previousElementSibling;
        const span = text_td.querySelector('span'); // 找到 <span> 元素
        const textarea = text_td.querySelector('textarea'); // 找到 <textarea> 元素
        const saveButton = btn_td.querySelector('.save-btn'); // 找到 儲存 按鈕
        const cancelButton = btn_td.querySelector('.cancel-btn'); // 找到 取消 按鈕
        const editButton = btn_td.querySelector('.edit-btn'); // 找到 編輯 按鈕
        const removeButton = btn_td.querySelector('.remove-btn'); // 找到 刪除 按鈕

        // 顯示 <span>、編輯和刪除按鈕
        span.style.display = 'inline';
        editButton.style.display = 'inline-block';
        removeButton.style.display = 'inline-block';

        // 隱藏 <textarea>、儲存和取消按鈕
        textarea.style.display = 'none';
        saveButton.style.display = 'none';
        cancelButton.style.display = 'none';
    })
})

newProjectBtn.addEventListener('click', function(e) {
    e.preventDefault();

    const new_project_html = `
        <div class="row g-3">
            <div class="col-md-12">
                <div class="form-floating">
                    <input type="text" class="form-control" id="floatingString" placeholder="new project name" name="project-name" required="">
                    <label for="floatingString">專案名稱</label>
                </div>
            </div>
            <div class="col-md-12">
                <div class="form-floating">
                    <input type="text" class="form-control" id="floatingString" placeholder="spec link" name="spec-link" required="">
                    <label for="floatingString">spec連結</label>
                </div>
            </div>
        </div>
    `;

    generateModalContent('new_project', new_project_html);
})

function new_project(project_name, spec_link) {
    project_name = project_name.trim();
    spec_link = spec_link.trim();
    if (!project_name || !spec_link) {
        alert("請完整輸入專案名稱和spec連結");
        return false;
    }

    data = {
        'project_name': project_name,
        'spec_link': spec_link,
    }

    fetch(`/${base_url}/proofread`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data),
    })
    .then(handle_response_status)
    .then(response => response.json())
    .then(data => {
        generateModalContent('alert', data.msg);
        $('#myModal').on('hidden.bs.modal', function () {
            location.reload();
        });
    })
    .catch(error => {
        generateModalContent('error', error)
    })
}

function search_proj(formData) {
    query_string = '';
    type = formData.get('type');
    content = formData.get('content').trim();
    if (content) {
        query_string += `?type=${type}&content=${content}`
    }

    window.location.href = url + query_string;
}

function remove_project(project_id) {
    fetch(`/${base_url}/proofread/${project_id}`, {
        method: 'DELETE',
    })
    .then(handle_response_status)
    .then(response => response.json())
    .then(data => {
        generateModalContent('alert', data.msg);
        $('#myModal').on('hidden.bs.modal', function () {
            location.reload();
        });
    })
    .catch(error => {
        generateModalContent('error', error)
    })
}

function update_project(formData) {
    project_id = +window.location.href.match(/(\d+)$/)[1];

    fetch(`/${base_url}/proofread/${project_id}`, {
        method: 'PATCH',
        body: formData,
    })
    .then(handle_response_status)
    .then(response => response.json())
    .then(data => {
        generateModalContent('alert', data.msg);
        $('#myModal').on('hidden.bs.modal', function () {
            location.reload();
        });
    })
    .catch(error => {
        generateModalContent('error', error)
    })
}

function insert_string(formData) {
    project_id = +window.location.href.match(/(\d+)$/)[1];

    fetch(`/${base_url}/proofread/${project_id}`, {
        method: 'POST',
        body: formData,
    })
    .then(handle_response_status)
    .then(response => response.json())
    .then(data => {
        generateModalContent('alert', data.msg);
        $('#myModal').on('hidden.bs.modal', function () {
            location.reload();
        });
    })
    .catch(error => {
        generateModalContent('error', error)
    })
}

function update_string(row, ps_id) {
    project_id = +window.location.href.match(/(\d+)$/)[1];
    const span = row.closest('td').previousElementSibling.children[0];
    const textarea = row.closest('td').previousElementSibling.children[1];
    if (textarea.textContent == textarea.value) {
        generateModalContent('alert', '無修改!');
        row.nextElementSibling.click();
        return false;
    }

    update_data = {
        'ps_id': ps_id,
        'string': textarea.value,
    }

    fetch(`/${base_url}/proofread/${project_id}/${ps_id}`, {
        method: 'PATCH',
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(update_data),
    })
    .then(handle_response_status)
    .then(response => response.json())
    .then(data => {
        generateModalContent('alert', data.msg);
        $('#myModal').on('hidden.bs.modal', function () {
            textarea.textContent = textarea.value;
            span.textContent = textarea.value;
            row.nextElementSibling.click();
        });
    })
    .catch(error => {
        generateModalContent('error', error)
    })
    
}

function remove_string(row, ps_id) {
    project_id = +window.location.href.match(/(\d+)$/)[1];
    const tr = row.closest('tr');
    console.log(tr);
    fetch(`/${base_url}/proofread/${project_id}/${ps_id}`, {
        method: 'DELETE',
    })
    .then(handle_response_status)
    .then(response => response.json())
    .then(data => {
        generateModalContent('alert', data.msg);
        $('#myModal').on('hidden.bs.modal', function () {
            tr.remove();
        });
    })
    .catch(error => {
        generateModalContent('error', error)
    })
}

function proofread_finished() {
    project_id = +window.location.href.match(/(\d+)$/)[1];

    fetch(`/${base_url}/proofread/updateReviewer/${project_id}`, {
        method: 'PATCH',
    })
    .then(handle_response_status)
    .then(response => response.json())
    .then(data => {
        generateModalContent('alert', data.msg);
    })
    .catch(error => {
        generateModalContent('error', error)
    })
}

function change_person_in_charge() {
    project_id = +window.location.href.match(/(\d+)$/)[1];

    fetch(`/${base_url}/proofread/updatePersonInCharge/${project_id}`, {
        method: 'PATCH',
    })
    .then(handle_response_status)
    .then(response => response.json())
    .then(data => {
        generateModalContent('alert', data.msg);
    })
    .catch(error => {
        generateModalContent('error', error)
    })
}

function get_log() {
    project_id = +window.location.href.match(/(\d+)$/)[1];

    fetch(`/${base_url}/proofread/log/${project_id}`, {
        method: 'GET',
    })
    .then(handle_response_status)
    .then(response => response.json())
    .then(data => {
        console.log(data);
        generateModalContent('diff', data);
    })
    .catch(error => {
        generateModalContent('error', error)
    })
}

function createDiffTable(data) {
    diffTablehtml = `<table class="table translations-table table-bordered">
                    <thead>
                        <tr>
                            <th scope="col" id="log_id">log_id</th>
                            <th scope="col" id="type">type</th>
                            <th scope="col" id="old_trans">舊字串</th>
                            <th scope="col" id="new_trans">現在字串</th>
                            <th scope="col" id="time">時間</th>
                        </tr>
                    </thead>
                    <tbody>
                    ${Object.entries(data)
                            .sort((a, b) => b[0] - a[0]) // 按照key（數字）從大到小排序
                            .map(([key, item]) => `
                            <tr>
                                <td>${key}</td>
                                <td>${item.type}</td>
                                <td>
                                    <span class="translation-text">${item.old_string}</span>
                                </td>
                                <td>
                                    <span class="translation-text">${item.new_string}</span>
                                </td>
                                <td>${item.time}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>`
	return diffTablehtml;
}

function download_excel() {
    project_id = +window.location.href.match(/(\d+)$/)[1];

    fetch(`/${base_url}/proofread/download/${project_id}`, {
        method: 'POST',
    })
    .then(handle_response_status)
    .then(response =>  {
        const contentType = response.headers.get('Content-Type');
        if (contentType && contentType.includes('application/json')) {
            return response.json().then(data => {
                if (!response.ok) {
                    let errorMessage;
                    errorMessage = data.msg || 'Resource not found';
                    throw new Error(errorMessage);
                }
            });
        }

        if (contentType && contentType.includes('application/zip')) {
            return response.blob();
        }
        throw new Error('無法識別回應格式');
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob); // Create a URL for the Blob
        const a = document.createElement('a'); // Create a link element
        a.href = url;
        a.download = `proofread_${project_id}.zip`;
        document.body.appendChild(a); // Append to the body
        a.click(); // Programmatically click the link to trigger the download
        a.remove(); // Remove the link from the document
        window.URL.revokeObjectURL(url); // Clean up the URL object
    })
    .catch(error => {
        generateModalContent('error', error)
    })
}