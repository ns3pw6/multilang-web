const searchNotFillCheck = document.getElementById('notFillCheck');
const caseSensitiveCheck = document.getElementById('case-sensitiveCheck');
const appLanguageSelect = document.getElementById('appLanguageSelect');
const stringSearchSelectApp = document.getElementById('stringSearchSelectApp');
const appSearchSelectApp = document.getElementById('appSearchSelectApp');
const resetBtns = document.getElementsByClassName("btn btn-secondary");
const searchResults = document.getElementById('searchResults');
const searchResultsTable = document.getElementById('searchResults-table');
const forms = document.querySelectorAll('form');
const searchResultsDownloadBtn = document.getElementById('searchResults-download-btn');
const platform = document.getElementsByClassName('platform-select')
const base_url = get_base_url();

initialize();
searchResults.style.visibility = "hidden";
var keeped_search_results = {};
var search_app_id = -1;

// Event listener for the checkbox change to enable/disble language select.
searchNotFillCheck.addEventListener('click', function() {
    if (searchNotFillCheck.checked === true) {
        appLanguageSelect.disabled = false;
    }
    else {
        appLanguageSelect.disabled = true;
    }
})

searchResultsDownloadBtn.addEventListener('click', function() {
    const download_language_select = `
        <select id="countries" name="countries" data-placeholder="請選擇輸出語言" multiple data-multi-select>
            ${Object.entries(languageMap)
                .map(([key, [englishName, localName]]) => 
                    `<option value="${key}">${localName}</option>`
                )
                .join('')}
        </select>
    `;
    generateModalContent('d_search', download_language_select)
    languageMultiSelect = new MultiSelect(document.getElementById('countries'));
})

// Language mapping
const languageMap = {
    // 'en-US': ['English', '英文'],
    'zh-TW': ['Traditional Chinese', '繁體中文'],
    'zh-CN': ['Simplified Chinese', '簡體中文'],
    'de-DE': ['German', '德文'],
    'ja-JP': ['Japanese', '日文'],
    'it-IT': ['Italian', '義大利文'],
    'fr-FR': ['French', '法文'],
    'nl-NL': ['Dutch', '荷蘭文'],
    'ru-RU': ['Russian', '俄文'],
    'ko-KR': ['Korean', '韓文'],
    'pl': ['Polish', '波蘭文'],
    'cs': ['Czech', '捷克文'],
    'sv': ['Svenska', '瑞典文'],
    'da': ['Dansk', '丹麥文'],
    'no': ['Norsk', '挪威文'],
    'fi': ['Suomi', '芬蘭文'],
    'pt': ['Portugal', '葡萄牙文'],
    'es': ['Spanish', '西班牙文'],
    'hu': ['Hungarian', '匈牙利文'],
    'tr': ['Turkish', '土耳其文'],
    'es-latino': ['Spanish - Latino America', '西班牙文 - 拉丁美洲'],
    'th': ['Thai', '泰文']
};

Array.from(resetBtns).forEach(function(btn) {
    btn.addEventListener('click', function() {
        initialize();
    });
});

Array.from(platform).forEach(function(platform) {
    platform.addEventListener('change', function() {
        let platform_id = platform.value;
        let appList = platform.parentNode.parentNode.nextElementSibling.firstElementChild.firstElementChild;
        initAppList(appList)

        get_apps(platform_id)
        .then(handle_response_status)
        .then(response => response.json())
        .then(function (data) {
            const sortedKeys = sortAppList(data);

            sortedKeys.forEach(function (key) {
                let newNode = document.createElement('option');
                newNode.value = key;
                newNode.textContent = data[key];
                appList.appendChild(newNode);
            }); 
        })
        .catch(error => {
            generateModalContent('error', error)
        })
    })
})

function initialize() {
    document.forms['stringid-form'].reset();
    document.forms['string-form'].reset();
    document.forms['namespace-form'].reset();
    document.forms['app-form'].reset();
    initAppList(stringSearchSelectApp);
    initAppList(appSearchSelectApp)
    appLanguageSelect.disabled = true;
}

document.addEventListener('DOMContentLoaded', function() {
    const searchContent = document.getElementById('searchContent');
    

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            search_app_id = -1;

            const activeTab = searchContent.querySelector('.tab-pane.active');
            if (!activeTab.contains(form)) {
                return;
            }
            
            const formData = new FormData(form);
            const searchType = form.id.split('-')[0];
            if (searchType === 'app') {
                if (form[0].value === "-1" || form[1].value === "-1") {
                    generateModalContent('alert', '請選擇平台和App')
                    return;
                }
                search_app_id = parseInt(form[1].value);
            }
            else{
                if (form[0].value === "") {
                    generateModalContent('alert', '請輸入搜尋內容')
                    return;
                }
            }
            var submitBtn = form.querySelector('form button[type="submit"]');
            searchResults.style.visibility = "hidden";
            disableBtn(submitBtn);
            formData.append('search_type', searchType);
            getStringData(formData, searchType, submitBtn);
            
        });
    });
});

function getStringData(formData, searchType, submitBtn) {
    fetch(`/${base_url}/search`, {
        method: 'POST',
        body: formData
    })
    .then(handle_response_status)
    .then(response => response.json())
    .then(data => {
        rowCount = 0; 
        startIndex = 0; 
        keeped_search_results = data['data'];
        createSearchResultsTable(data['data'], searchType);
    })
    .catch(error => {
        generateModalContent('error', error)
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerText = "搜尋";
    });
}

function createTableHeader(search_type) {
    let headerText = [];
    if(search_type === 'namespace') {
        headerText = ['#', 'String ID', 'String', 'namespace', 'Note'];
    }
    else {
        headerText = ['#', 'String ID', 'String', 'Note'];
    }
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    headerText.forEach((headerText, index) => {
        const th = document.createElement('th');
        if(index == 0) {
            th.style.textAlign = 'center';
        }
        th.textContent = headerText;
        th.setAttribute('scope', 'col');
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    searchResultsTable.appendChild(thead);
}

const scrollContainer = document.getElementById('scrollContainer');
let rowCount = 0; 
let batchSize = 50; 
let startIndex = 0; 

function createSearchResultsTable(data, search_type) {
    searchResultsTable.innerHTML = '';

    rowCount = Object.keys(data).length;
    createTableHeader(search_type);
    createVisibleRows(data, search_type);

    scrollContainer.addEventListener('scroll', () => {
        const { scrollTop, clientHeight, scrollHeight } = scrollContainer;
        if (scrollTop + clientHeight >= scrollHeight) {
            loadMoreRows(data, search_type); 
        }
    });

    searchResults.style.visibility = 'visible';
}

function createVisibleRows(data, search_type) {
    const tbody = document.createElement('tbody');
    
    const endIndex = Math.min(startIndex + batchSize, rowCount);
    Object.entries(data).slice(startIndex, endIndex).forEach(([key, item], _) => {
        const row = document.createElement('tr');
        row.classList.add('accordion-toggle', 'collapsed');
        row.dataset.key = key;
        row.setAttribute('id', `accordion${key}`);
        row.style.cursor = 'pointer';

        if (search_type === 'namespace') {
            row.innerHTML = `
                <td class="expand-button"></td>
                <td id="stringIDcol">${key}</td>
                <td>${item.translations['en-US'] || ''}</td>
                <td>${item.namespace || ''}</td>
                <td>${item.note || ''}</td>
            `;
        } else {
            row.innerHTML = `
                <td class="expand-button"></td>
                <td id="stringIDcol">${key}</td>
                <td id="stringContent">${item.translations['en-US'] || ''}</td>
                <td>${item.note || ''}</td>
            `;
        }

        tbody.appendChild(row);
    });

    tbody.addEventListener('click', function(event) {
        const row = event.target.closest('tr');
        if (!row) return;

        if (row.classList.contains('accordion-toggle')) {
            handleRowToggle(row, data);
        }
    });

    searchResultsTable.appendChild(tbody);
    startIndex = endIndex;
}

function loadHiddenRow(row, key, item) {
    const hiddenRow = document.createElement('tr');
    hiddenRow.classList.add('hide-table-padding');

    const hiddenCell = document.createElement('td');
    hiddenCell.colSpan = item.namespace ? 5 : 4;
    var remove_string = ``;

    if (search_app_id !== -1) {
        remove_string = `<button type="button" class="btn btn-warning" data-bs-toggle="modal" data-bs-target="#myModal" onclick="removeAppString(this)">
                            <i class="bi bi-trash me-1"></i>
                            下架此App字串對應的namespace
                        </button>`;
    }

    hiddenCell.innerHTML = `
        <div id="collapse_${key}" class="row g-3 in p-3 collapse show"> 
        <div>該字串使用於: ${item['app']}</div>
        <div>
            <button type="button" class="btn btn-info" data-bs-toggle="modal" data-bs-target="#myModal" onclick="getDiff(this)">
                <i class="bi bi-info-circle me-1"></i>
                查看字串更新紀錄
            </button>
            ${remove_string}
        </div>
        <table class="table translations-table table-bordered" data-string-id="${key}">
            <thead>
                <tr>
                        <th scope="col" id="lang">語言</th>
                        <th scope="col" id="translation">翻譯</th>
                        <th scope="col" id="modifyString">修改</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Note</td>
                    <td>
                        <div class="string">${item.note || ''}</div>
                    </td>
                    <td>
                        <button class="btn btn-primary btn-sm edit-btn" onclick="editRow(this)">Edit</button>
                    </td>
                </tr>
                ${Object.keys(languageMap).map(lang => `
                    <tr>
                        <td data-langtag="${lang}">${languageMap[lang][0]}(${lang})<br>(${languageMap[lang][1]})</td>
                        <td>
                            <div class="string">${item.translations[lang] || ''}</div>
                        </td>
                        <td class="text-center">
                            <button class="btn btn-primary btn-sm edit-btn" onclick="editRow(this)">Edit</button>
                        </td>
                    </tr>
                `).join('')}
                <tr>
                        <td colspan="${item.namespace ? 5 : 4}" style="text-align: center;">
                            <button class="btn btn-secondary" onclick="collapseRow(this)">收起</button>
                        </td>
                    </tr>
            </tbody>
        </table>
        </div>
    `;

    hiddenRow.appendChild(hiddenCell);
    row.insertAdjacentElement('afterend', hiddenRow);
}

// 新增處理展開/收合的函數
function handleRowToggle(row, data) {
    if (row.dataset.animating === 'true') return;
    row.dataset.animating = 'true';

    const key = row.dataset.key;
    const tdAction = row.querySelector('.expand-button');
    const hiddenRow = row.nextElementSibling;
    
    tdAction.classList.toggle('expanded');

    if (!row.classList.contains('collapsed')) {
        // Collapse
        if (hiddenRow && hiddenRow.classList.contains('hide-table-padding')) {
            const rowHeight = hiddenRow.scrollHeight;
            hiddenRow.style.height = rowHeight + 'px';
            hiddenRow.offsetHeight; // Force reflow
            hiddenRow.classList.add('collapsed');
            hiddenRow.style.height = '0';
            
            setTimeout(() => {
                hiddenRow.remove();
                row.classList.add('collapsed');
                row.dataset.animating = 'false'
            }, 300);
        } else {
            row.classList.add('collapsed');
            row.dataset.animating = 'false';
        }
    } else {
        // Expand
        loadHiddenRow(row, key, data[key]);
        row.classList.remove('collapsed');
        const newHiddenRow = row.nextElementSibling;
        if (newHiddenRow) {
            newHiddenRow.classList.add('collapsed');
            newHiddenRow.offsetHeight; // Force reflow
            newHiddenRow.classList.remove('collapsed');
        }
        setTimeout(() => {
            row.dataset.animating = 'false';
        }, 300);
    }
}

// 修改 collapseRow 函數
function collapseRow(btn) {
    const hiddenRow = btn.closest('.hide-table-padding');
    const parentRow = hiddenRow.previousElementSibling;
    
    if (!hiddenRow || parentRow.dataset.animating === 'true') return;
    parentRow.dataset.animating = 'true';

    const tdAction = parentRow.querySelector('.expand-button');
    tdAction.classList.remove('expanded');
    
    const rowHeight = hiddenRow.scrollHeight;
    hiddenRow.style.height = rowHeight + 'px';
    hiddenRow.offsetHeight; // Force reflow
    hiddenRow.classList.add('collapsed');
    hiddenRow.style.height = '0';
    
    setTimeout(() => {
        if (hiddenRow.parentNode) {
            hiddenRow.remove();
            parentRow.classList.add('collapsed');
            parentRow.dataset.animating = 'false'
        }
    }, 300);
}

function loadMoreRows(data, search_type) {
    if (startIndex < rowCount) {
        createVisibleRows(data, search_type);
    }
}

function editRow(btn) {
    const row = btn.closest('tr');
    const translationCell = row.querySelector('.string');
    const langTagCell = row.querySelector('td:first-child');
    const langTag = langTagCell.dataset.langtag || 'note';

    if (btn.textContent === 'Edit') {
        const currentText = translationCell.textContent.trim();
        btn.setAttribute('data-original-text', currentText);
        translationCell.innerHTML = `
            <textarea class="form-control">${currentText}</textarea>
        `;
        btn.textContent = 'Save';
    } else if (btn.textContent === 'Save') {
        const textarea = translationCell.querySelector('textarea');
        const updatedText = textarea.value.trim();

        if (btn.getAttribute('data-original-text') === updatedText) {
            translationCell.textContent = btn.getAttribute('data-original-text');
            btn.textContent = 'Edit';
            return;
        }

        const stringId = row.closest('table').dataset.stringId;
        updateTranslation(stringId, langTag, updatedText, btn, translationCell);
    }
}

function updateTranslation(string_id, lang_tag, updated_text, btn, translationCell) {
    const update_data = {
        'str_id': string_id,
        'lang_tag': lang_tag,
        'content': updated_text
    }

    fetch(`/${base_url}/update`, {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(update_data),
    })
    .then(handle_response_status)
    .then(response => response.json())
    .then((responseText) => {
        if (responseText.test_mode == true) {
            generateModalContent('alert', responseText.msg);
            return;
        }

        if (responseText["msg"] == "Update successful" || 
            responseText["msg"] == "Note Update successful") {
            generateModalContent('alert', '更新成功！');
            translationCell.textContent = updated_text;
            if (lang_tag === 'note') {
                keeped_search_results[string_id].note = updated_text;
                const noteCol = btn.closest('table').closest('tr').previousSibling.lastElementChild;
                noteCol.textContent = updated_text;
            }
        }
        else {
            generateModalContent('error', responseText["msg"]);
            const originalText = btn.getAttribute('data-original-text');
            translationCell.textContent = originalText;
        }
        btn.textContent = 'Edit';
    })
    .catch((error) => {
        generateModalContent('error', error);
        const originalText = btn.getAttribute('data-original-text');
        translationCell.textContent = originalText;
        btn.textContent = 'Edit';
    });
}

function getDiff(button) {
    const row = button.closest('tr'); // 獲取最近的 tr 元素
    const dataKey = row.previousSibling.dataset.key; // 獲取 data-key 值
    getStringDiff(dataKey);
}

function getStringDiff(str_id) {
    fetch(`/${base_url}/search/log/${str_id}`, {
        method: 'POST',
    })
    .then(handle_response_status)
    .then(response => response.json())
    .then(data => {
        generateModalContent('diff', data['data']);
    })
    .catch(error => {
        generateModalContent('error', error)
    })
}

function createDiffTable(data) {
    diffTablehtml = `<table class="table translations-table table-bordered">
                    <thead>
                        <tr>
                            <th scope="col" id="lang">語言</th>
                            <th scope="col" id="old_trans">舊字串</th>
                            <th scope="col" id="new_trans">現在字串</th>
                            <th scope="col" id="modifyString">復原</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.map(item => `
                            <tr>
                                <td>${item.lang_name}</td>
                                <td>
                                    <span class="translation-text">${item.old_value}</span>
                                </td>
                                <td>
                                    <span class="translation-text">${item.new_value}</span>
                                </td>
                                <td>
                                    <button class="btn btn-primary edit-btn" onclick="recoverString(${item.str_id}, ${item.lang_id})">復原</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>`
	return diffTablehtml;
}

function recreateTable(str_id, lang_id, string) {
    var index = parseInt(lang_id, 10);
    const target_row_data = document.getElementById(`collapse_${str_id}`).querySelector('tbody').children[index-1].children[1];
    var textSpan = target_row_data.children[0];
    var textArea = target_row_data.children[1];
    textSpan.textContent = string;
    textArea.value = string;
}

function recoverString(str_id, lang_id) {

    if (!confirm('確定要回復嗎？')) {
        return;
    }

    fetch(`/${base_url}/update`, {
        method: 'PATCH',
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            'str_id': str_id,
            'lang_id': lang_id
        })
    })
    .then(handle_response_status)
    .then(response => response.json())
    .then(data => {
        if (data.test_mode == true) {
            generateModalContent('alert', data.msg);
            return;
        }
        if(data['msg'] === 'success') {
            alert('復原字串成功!!');
            getStringDiff(str_id);
            recreateTable(str_id, lang_id, data['old_content']);
        }
        else {
            generateModalContent('error', data['msg']);
        }
    })
    .catch(error => {
        generateModalContent('error', error)
    })
}

function getSelectedLanguages() {
    if (!languageMultiSelect) {
        console.error('Language MultiSelect not initialized');
        return [];
    }
    return languageMultiSelect.selectedValues;
}

function downloadExcel() {
    var selectedLanguages = getSelectedLanguages();
    if (selectedLanguages.length == 0) {
        alert('請選擇語言!');
        return;
    }
    selectedLanguages = ['en-US', ...selectedLanguages];
    
    data = {
        'strings': keeped_search_results,
        'selectedLanguages': selectedLanguages
    }

    var downloadBtn = document.getElementById('downloadBtn');
    disableBtn(downloadBtn);

    fetch(`/${base_url}/download/search`, {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data)
    })
    .then(handle_response_status)
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'search_strings.zip';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        $('#myModal').modal('hide');
    })
    .catch(error => {
        generateModalContent('error', error)
    })
    .finally (() => {
        downloadBtn.disabled = false;
        downloadBtn.innerText = "下載";
    })
}

function removeAppString(button) {
    const row = button.closest('tr'); // 獲取最近的 tr 元素
    const dataKey = parseInt(row.previousSibling.dataset.key); // 獲取 data-key 值
    getNamespaces(search_app_id, dataKey);
}

function getNamespaces(app_id, str_id) {
    fetch(`/${base_url}/search/${app_id}/${str_id}`, {
        method: 'POST'
    })
    .then(handle_response_status)
    .then(response => response.json())
    .then(data => {
        const remove_namespace_select = `
            <select id="remove-namespace" class="form-select" data-placeholder="請選擇下架namespace">
                ${Object.entries(data)
                    .map(([key, value]) => 
                        `<option value="${key}">${value}</option>`
                    )
                    .join('')}
            </select>`;
        generateModalContent('remove', remove_namespace_select);
    })
    .catch(error => {
        generateModalContent('error', error)
    })
}

function removeString(asn_id) {
    fetch(`/${base_url}/update/${asn_id}`, {
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
