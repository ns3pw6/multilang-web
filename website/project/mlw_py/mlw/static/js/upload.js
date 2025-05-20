const selectPlatform = document.getElementById("selectedPlatform");
const selectApp = document.getElementById("selectedApp");
const svnUploadForm = document.getElementById("svn-upload");
const excelUploadForm = document.getElementById("excel-upload");
const uploadCard = document.getElementById("upload-card");
const excelUploadBlock = document.getElementById("excel-upload-block");
const insertTable = document.getElementById("insert-table");
const updateTable = document.getElementById("update-table");
const removeTable = document.getElementById("remove-table");
const excelUploadError = document.getElementById("excel-upload-error");
const insertSelectAll = insertTable.getElementsByClassName("select-all")[0];
const updateSelectAll = updateTable.getElementsByClassName("select-all")[0];
const removeSelectAll = removeTable.getElementsByClassName("select-all")[0];
const forms = document.querySelectorAll('form');
const base_url = get_base_url();

var uploadFileNameArray = new Array();
tableData = { insert: {}, update: {}, remove: {} };

initialize();
uploadCard.style.display = "none";
excelUploadBlock.style.display = "none";

selectPlatform.addEventListener("change", (e) => {
    e.preventDefault();
    p_id = selectPlatform.value;
    initialize();

    selectPlatform.value = p_id;
    get_apps(p_id)
    .then(handle_response_status)
    .then(response => response.json())
    .then((data) => {
        const sortedKeys = sortAppList(data);
        sortedKeys.forEach(function (key) {
            let newNode = document.createElement("option");
            newNode.value = key;
            newNode.textContent = data[key];
            selectApp.append(newNode);
        });
    })
    .catch(error => {
        generateModalContent('error', error)
    });
});

function initialize() {
    forms.forEach(form => {
        form.reset();
    })
    initAppList(selectApp)
    progressArea.style.display = "none";
    uploadedArea.style.display = "none";
    resetSelected();
}

function resetSelected() {
    selectall = document.getElementsByClassName("select-all");
    Object.values(selectall).forEach((input) => {
        input.children[0].checked = false;
    });
}

function handleOptionChange(selectElement) {
    const selectedValue = selectElement.value;
    const inputField = selectElement.nextElementSibling; // Textbox is the next sibling element

    if (selectedValue === "-1") {
        inputField.classList.remove("d-none"); // Show the textbox
    } else {
        inputField.classList.add("d-none"); // Hide the textbox
    }
}

function createTableRows(data, remove = false) {
    let html = "";
    i = 1;
    if (remove) {
        for (key in data) {
            html += `<tr>`;
            html += `<th scope="row"><input type="checkbox" class="rowCheckbox" data-id="${i}"></th>`;
            html += `<td n-id="${key}">${data[key]}</td>`;
            html += `</tr>`;
            ++i;
        }
    } else {
        for (let key in data) {
            html += `<tr>`;
            html += `<td scope="row"><input type="checkbox" class="rowCheckbox" data-id="${i}"></td>`;
            html += `<td ${data[key].hasOwnProperty('namespace_id') ? `n-id=${data[key]['namespace_id']}` : ""}>${key}</td>`;
            for (let prop in data[key]) {
                if (prop === "options") {
                    const options = data[key][prop];
                    html += `<td><div class="row g-3"><div class="col-md-12">`;

                    // Create select element
                    html += `<select class="form-select" onchange="handleOptionChange(this)">`;

                    // Populate options
                    let defaultSelected = true;
                    if (options.length !== 0) {
                        options.forEach((option) => {
                            html += `<option value="${option.str_id}">${option.formatted_string}</option>`;
                            if (defaultSelected) {
                                defaultSelected = false;
                            }
                        });
                    }

                    // Add "新增一個" option
                    html += `<option value="-1" ${defaultSelected ? "selected" : ""}>新增一個</option>`;
                    html += `</select>`;

                    // Add a hidden textbox
                    html += `<input type="text" class="form-control ${defaultSelected ? "" : "d-none"}" placeholder="請在此輸入對應中文" spellcheck="true"/>`;
                    html += `</div></div></td>`;
                } else if (prop === 'namespace_id' || prop === 'str_id') {
                    continue;
                } else {
                    html += `<td data-str_id="${data[key].hasOwnProperty('str_id') ? data[key]['str_id'] : "-1"}">${data[key][prop]}</td>`;
                }
            }
            html += `</tr>`;
            ++i;
        }
    }

    return html;
}

function renderTables(data) {
    insertTable.getElementsByTagName("tbody")[0].innerHTML = createTableRows(
        data["insert"]
    );
    updateTable.getElementsByTagName("tbody")[0].innerHTML = createTableRows(
        data["update"]
    );
    removeTable.getElementsByTagName("tbody")[0].innerHTML = createTableRows(
        data["remove"],
        true
    );
}

insertSelectAll.addEventListener("change", (e) => {
    const isChecked = e.target.checked;
    const checkboxes = document.querySelectorAll(
        "#insert-table tbody .rowCheckbox"
    );
    checkboxes.forEach((checkbox) => {
        checkbox.checked = isChecked;
        // Update the tableData checkbox states
        const rowId = checkbox.dataset.id;
        tableData.insert[rowId] = isChecked;
    });
});

updateSelectAll.addEventListener("change", (e) => {
    const isChecked = e.target.checked;
    const checkboxes = document.querySelectorAll(
        "#update-table tbody .rowCheckbox"
    );
    checkboxes.forEach((checkbox) => {
        checkbox.checked = isChecked;
        // Update the tableData checkbox states
        const rowId = checkbox.dataset.id;
        tableData.update[rowId] = isChecked;
    });
});

removeSelectAll.addEventListener("change", (e) => {
    const isChecked = e.target.checked;
    const checkboxes = document.querySelectorAll(
        "#remove-table tbody .rowCheckbox"
    );
    checkboxes.forEach((checkbox) => {
        checkbox.checked = isChecked;
        // Update the tableData checkbox states
        const rowId = checkbox.dataset.id;
        tableData.remove[rowId] = isChecked;
    });
});

const insertSubmit = document.getElementById("insertBtn");
const updateSubmit = document.getElementById("updateBtn");
const removeSubmit = document.getElementById("removeBtn");

insertSubmit.addEventListener("click", (e) => {
    e.preventDefault();
    const checkboxes = document.querySelectorAll(
        "#insert-table tbody .rowCheckbox"
    );
    svn_submit("insert", checkboxes);
});

updateSubmit.addEventListener("click", (e) => {
    e.preventDefault();
    const checkboxes = document.querySelectorAll(
        "#update-table tbody .rowCheckbox"
    );
    svn_submit("update", checkboxes);
});

removeSubmit.addEventListener("click", (e) => {
    e.preventDefault();
    const checkboxes = document.querySelectorAll(
        "#remove-table tbody .rowCheckbox"
    );
    svn_submit("remove", checkboxes);
});

function svn_submit(type, checkboxes) {
    var data = {};
    data["app_id"] = app_id;
    data['datas'] = {};
    type_mapping = {
        insert: {
            method: "POST",
            zh: "新增",
        },
        update: {
            method: "PATCH",
            zh: "更新",
        },
        remove: {
            method: "DELETE",
            zh: "刪除",
        },
    };

    // 遍歷所有勾選框
    try {
        let has_checked_flag = false;
        var has_skip_item = false;
        var BreakException = {};
        checkboxes.forEach((checkbox) => {
            if (checkbox.checked) {
                // 獲取勾選框所在行的內容
                has_checked_flag = true;
                const row = checkbox.closest("tr");
                const cells = row.querySelectorAll("td");
                if (type === "insert") {
                    var str_id =
                        cells[3].firstChild.firstChild.children[0]
                            .selectedOptions[0].value;
                    var zh =
                        cells[3].firstChild.firstChild.children[0]
                            .selectedOptions[0].textContent;
                    if (str_id === "-1") {
                        zh = cells[3].firstChild.firstChild.children[1].value;
                        if (zh === "") {
                            // generateModalContent("alert", "新增字串時，中文選項不能為空\nNamespace: " + cells[1].textContent);
                            // throw BreakException;
                            has_skip_item = true;
                            return;
                        }
                    }
                    data['datas'][cells[1].textContent] = {};
                    data['datas'][cells[1].textContent]["en"] = cells[2].textContent;
                    data['datas'][cells[1].textContent]["str_id"] = str_id;
                    data['datas'][cells[1].textContent]["zh-TW"] = zh;
                } else if (type === "update") {
                    var str_id = cells[2].dataset.str_id;
                    data['datas'][cells[1].textContent] = {};
                    data['datas'][cells[1].textContent]["namespace_id"] = cells[1].attributes[0].value;
                    data['datas'][cells[1].textContent]["current_eng"] =
                        cells[2].textContent;
                    data['datas'][cells[1].textContent]["new_eng"] =
                        cells[3].textContent;
                    data['datas'][cells[1].textContent]["str_id"] = str_id;
                } else if (type === "remove") {
                    data['datas'][cells[0].attributes[0].value] = cells[0].textContent;
                }
            }
        });
        if (!has_checked_flag) {
            generateModalContent("alert", `請選擇要${type_mapping[type]["zh"]}的項目`)
            return;
        }
    } catch (e) {
        if (e === BreakException) {
            return;
        }
    }

    fetch(`/${base_url}/upload`, {
        method: type_mapping[type]["method"],
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    })
    .then(handle_response_status)
    .then(response => response.json())
    .then(function (data) {
        if (data["msg"] === "success") {
            if (data.test_mode == true) {
                generateModalContent("alert", data.test_msg)
            } else {
                // Remove checked rows
                checkboxes.forEach((checkbox) => {
                    if (checkbox.checked) {
                        const row = checkbox.closest("tr");
                        row.remove();
                    }
                });
                if (has_skip_item) {
                    generateModalContent("alert", `${type_mapping[type]["zh"]}部分資料成功!!`);
                }
                else {
                    generateModalContent("alert", `${type_mapping[type]["zh"]}成功!!`);
                }
            }
        } else {
            generateModalContent("error", data["msg"]);
        }
    })
    .catch((error) => {
        generateModalContent("error", error);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const activeTab = searchContent.querySelector('.tab-pane.active');
            if (!activeTab.contains(form)) {
                return;
            }

            const uploadType = form.id.split('-')[0];
            if (uploadType === 'svn') {
                submit_svn_form(form);
            }
            else {
                handle_uploaded_excel(form);
            }
        })
    }) 
})

let errorMessages = [];
const rowsPerLoad = 50;
let loadedRows = 0;

function render_excel_error(error_msg) {
    const errorBody = document.getElementById('excel-upload-error').querySelector('tbody');
    errorBody.innerHTML = ''; 
    errorMessages = error_msg;
    loadedRows = 0; // reset loaded rows
    document.getElementById('excel-upload-block').style.display = "block";

    // 初始可見行
    loadVisibleRows();

    const container = document.getElementById('excel-upload-error-container');
    container.addEventListener('scroll', loadVisibleRows);
        
}

function loadVisibleRows() {
    const container = document.getElementById('excel-upload-error-container');
    const scrollTop = container.scrollTop;
    const length = errorMessages.length * 24;
    const containerHeight = (length > 900) ? 900 : length;

    // count rows to show
    const visibleRows = Math.ceil(containerHeight / 30);
    const start = Math.floor(scrollTop / 30); // current scroll position
    
    // restrict load row
    const end = Math.min(start + visibleRows + 2, errorMessages.length); // load more data row

    // load rows
    const errorBody = document.getElementById('excel-upload-error').querySelector('tbody');
    for (let i = loadedRows; i < end; i++) {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${errorMessages[i]}</td>`;
        errorBody.appendChild(tr);
    }
    loadedRows = end; // update loaded row
}

function handle_uploaded_excel(form) {
    uploadCard.style.display = "none";
    const formData = new FormData(form);
    if (uploadFileNameArray.length === 0) {
        generateModalContent("error", "請先上傳檔案!")
        return;
    }
    const submitBtn = document.getElementById('excelString');
    disableBtn(submitBtn);

    return fetch(`/${base_url}/upload/excel`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            'force_update': formData.get('force-update') == 'on',
            'uploadFileNameArray': uploadFileNameArray,
        }),
    })
    .then(handle_response_status)
    .then(response => response.json())
    .then(data => {
        msg = ``;
        console.log(data.test_mode)
        if (data.test_mode == true) {
            msg += `<a style="color: red;"><strong>測試模式不會進行上傳!</strong></a><br>`;
        }
        msg += `上傳成功! ${data['count']} 筆資料已更新!`;
        if (data['msg'] === 'success') {
            excelUploadBlock.style.display = "none";
            generateModalContent("alert", msg);
        }
        else if (Array.isArray(data['msg'])) {
            render_excel_error(data['msg']);
            msg += `請確認剩下錯誤訊息!`;
            generateModalContent("alert", msg);
        }
        else {
            generateModalContent("error", data['msg'])
        }
    })
    .catch(error => {
        generateModalContent("error", error)
    })
    .finally(() => {
        uploadedArea.innerHTML = "";
        uploadFileNameArray = new Array();
        submitBtn.disabled = false;
        submitBtn.innerText = "上傳";
    });
}

function submit_svn_form(form) {
    platform_id = form[0].value;
    app_id = form[1].value;
    platform_name = form[0].selectedOptions[0].text;
    app_name = form[1].selectedOptions[0].text;

    if (!check_platform_and_app_select(platform_id, app_id)) {
        return;
    }

    const data = {};
    data[platform_id] = platform_name;
    data[app_id] = app_name;

    var submitBtn = form.querySelector('form button[type="submit"]');
    disableBtn(submitBtn)

    fetch_svn_upload(data, platform_id, app_id).finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerText = "送出";
    });
}

function fetch_svn_upload(data, platform_id, app_id) {
    excelUploadBlock.style.display = "none";

    return fetch(`/${base_url}/upload/${parseInt(platform_id)}/${parseInt(app_id)}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    })
    .then(handle_response_status)
    .then(response => response.json())
    .then(function (response_data) {
        renderTables(response_data);
        uploadCard.style.display = "block";
    })
    .catch((error) => {
        generateModalContent("error", error)
    })
}