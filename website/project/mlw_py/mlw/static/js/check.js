const selectPlatform = document.getElementById("selectedPlatform");
const selectApp = document.getElementById("selectedApp");
const resultArea = document.getElementById("check-card");
const forms = document.querySelectorAll('form');
const submitBtn = document.getElementById("checkBtn");
const checkResultsTable = document.getElementById('checkResultsTable');
const base_url = get_base_url();

let langTagMap =
{
	'en-US': '英文',
	'zh-TW': '繁體中文',
	'zh-CN': '簡體中文',
	'de-DE': '德文',
	'ja-JP': '日文',
	'it-IT': '義大利文',
	'fr-FR': '法文',
	'nl-NL': '荷蘭文',
	'ru-RU': '俄文',
	'ko-KR': '韓文',
	'pl': '波蘭文',
	'cs': '捷克文',
	'sv': '瑞典文',
	'da': '丹麥文',
	'no': '挪威文',
	'fi': '芬蘭文',
	'pt': '葡萄牙文',
	'es': '西班牙文',
	'hu': '匈牙利文',
	'tr': '土耳其文',
	'es-latino': '西班牙文 - 拉丁美洲',
	'th': '泰文'
}

initialize()

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
    }
    )
    .catch(error => {
        generateModalContent('error', error)
    })
});

document.addEventListener('DOMContentLoaded', function() {
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(form);
            app_id = formData.get('select-app');
            if (app_id == null) {
                generateModalContent('error', '請選擇App!');
                return;
            }

            checkAppStringFormat(app_id);
        });
    });
})

function initialize() {
    forms.forEach(form => {
        form.reset();
    })
    initAppList(selectApp)
    resetSelected();
}

function resetSelected() {
    selectall = document.getElementsByClassName("select-all");
    Object.values(selectall).forEach((input) => {
        input.children[0].checked = false;
    });
}

function checkAppStringFormat(app_id) {
    disableBtn(submitBtn);
    resultArea.style.display = "none";

    fetch(`/${base_url}/check/${app_id}`, {
        method: 'POST',
    })
    .then(handle_response_status)
    .then(response => response.json())
    .then(data => {
        if(Object.keys(data.msg).length > 0) {
            generateModalContent('alert', '請確認以下錯誤字串!');
            resultArea.style.display = "block";
            renderCheckResultTable(data.msg);
        } else {
            generateModalContent('alert', '無錯誤!');
        }
    })
    .catch(error => {
        generateModalContent('error', error);
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerText = "檢查";
    });;
}

function renderCheckResultTable(data) {
    checkResultsTable.innerHTML = '';

    createTableHeader();
    createVisibleRows(data);
}

function createTableHeader() {
	let headerText = ['#', 'String ID', 'String'];
	let columnWidths = ['3%', '7%', '90%'];
	const thead = document.createElement('thead');
	const headerRow = document.createElement('tr');
	headerText.forEach((text, index) => {
		const th = document.createElement('th');
		th.textContent = text;
		th.style.width = columnWidths[index];
        if (index === 0) {
            th.style.textAlign = 'center';
        }
        th.setAttribute('scope', 'col');
		headerRow.appendChild(th);
	});
	thead.appendChild(headerRow);
	checkResultsTable.appendChild(thead);
}

function createVisibleRows(data) {
    const tbody = document.createElement('tbody');

    for (const str_id in data) {
        const parentRow = document.createElement('tr');
        parentRow.classList.add('accordion-toggle', 'collapsed');
        parentRow.dataset.key = str_id;
        parentRow.style.cursor = 'pointer';

        parentRow.innerHTML = `
            <td class="expand-button"></td>
            <td id="stringIDcol">${str_id}</td>
            <td id="stringContent">${escapeHtml(data[str_id]['en-US']) || ''}</td>
        `;

        tbody.appendChild(parentRow);

        const childRow = document.createElement('tr');
        childRow.style.display = 'none';
        childRow.className = 'hide-table-padding';
        const childTd = document.createElement('td');
        childTd.colSpan = 3;
        childTd.innerHTML = loadHiddenRow(data[str_id], str_id);
        childRow.appendChild(childTd);
        tbody.appendChild(childRow);
    }

    toggleCollapse(tbody);
    checkResultsTable.appendChild(tbody);
}

function loadHiddenRow(data, str_id) {
    let content = `
    <div id="collapse_${str_id}" class="row g-3 in p-3 collapse show"> 
    <table class="table translations-table table-bordered" style="width: 100%;" data-string-id="${str_id}">`;
    content += `
        <thead>
            <tr>
                <th scope="col" style="width: 10%;">語言</th>
                <th scope="col" style="width: 15%;">錯誤訊息</th>
                <th scope="col" style="width: 70%;">翻譯</th>
                <th scope="col" style="width: 5%;">修改</th>
            </tr>
        </thead>
        <tbody>
    `;

    for (const langTag in data) {
        if (langTag === 'en-US') continue;

        const errorMsg = data[langTag].error_msg || '無錯誤';
        const stringContent = data[langTag].string || '';

        content += `
            <tr>
                <td data-langtag="${langTag}">${langTag}<br>
				(${langTagMap[langTag]})</td>
                <td>${errorMsg}</td>
                <td>
                    <div class="string">${escapeHtml(stringContent)}</div>
                </td>
                <td class="text-center">
                    <button class="btn btn-primary btn-sm edit-btn" onclick="editRow(this)">Edit</button>
                </td>
            </tr>
        `;
    }

    content += '</tbody></table></div>';
    return content;
}

function escapeHtml(str) {
    return str.replace(/[&<>"']/g, function(match) {
        const escapeChars = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        };
        return escapeChars[match];
    });
}

function toggleCollapse(tbody) {
    tbody.addEventListener('click', (event) => {
        const parentRow = event.target.closest('.accordion-toggle');
        if (parentRow) {
            const tdAction = parentRow.querySelector('td');
            const childRow = parentRow.nextElementSibling;
            const isExpanded = tdAction.classList.contains('expanded');

            // Toggle expand button
            tdAction.classList.toggle('expanded');

            // Animate child row
            if (isExpanded) {
                // Collapse
                const rowHeight = childRow.scrollHeight;
                childRow.style.height = rowHeight + 'px';
                // Force reflow
                childRow.offsetHeight;
                childRow.classList.add('collapsed');
                childRow.style.height = '0';
                
                // Remove after animation
                setTimeout(() => {
                    childRow.style.display = 'none';
                    childRow.style.height = '';
                    childRow.classList.remove('collapsed');
                }, 300);
            } else {
                // Expand
                childRow.style.display = 'table-row';
                childRow.classList.add('collapsed');
                // Force reflow
                childRow.offsetHeight;
                childRow.classList.remove('collapsed');
            }
        }
    });
}

function editRow(btn) {
    const row = btn.closest('tr');
    const translationCell = row.querySelector('.string');
    const langTagCell = row.querySelector('td:first-child');
    

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
        const langTag = langTagCell.dataset.langtag.trim();

        if (btn.getAttribute('data-original-text') === updatedText) {
            translationCell.textContent = btn.getAttribute('data-original-text');
            btn.textContent = 'Edit';
            return;
        }

        translationCell.textContent = updatedText;
        btn.textContent = 'Edit';

        const stringId = row.closest('table').dataset.stringId;
        updateTranslation(stringId, langTag, updatedText, btn, translationCell);
    }
}

function removeRow(btn) {
    const childRow = btn.closest('tr');
    const tbody = childRow.closest('tbody');
    childRow.remove();

    // 如果 tbody 中沒有其他子行，移除 parent-row
    if (tbody.querySelectorAll('tr').length === 0) {
        const childRow = tbody.closest('.hide-table-padding');
        const parentRow = childRow.previousElementSibling;
        childRow.remove();
        parentRow.remove();
    }
}

function updateTranslation(string_id, lang_tag, updated_text, btn, translationCell) {
    update_data = {
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
        if (responseText["msg"] == "Update successful") {
            generateModalContent('alert', '更新成功！');
            translationCell.textContent = updated_text;
            removeRow(btn);
        }
        else {
            generateModalContent('error', responseText["msg"]);
            const originalText = btn.getAttribute('data-original-text');
            translationCell.textContent = originalText;
            btn.textContent = 'Edit';
        }
    })
    .catch((error) => {
        generateModalContent('error', error)

        const originalText = btn.getAttribute('data-original-text');
        translationCell.textContent = originalText;
        btn.textContent = 'Edit';
    });
}

function downloadExcel() {
    const rows = [];
    const table = document.querySelectorAll('.translations-table tbody tr');
    table.forEach(row => {
        const stringId = row.closest('table').dataset.stringId;
        const langTag = row.querySelector('td[data-langtag]').dataset.langtag.trim();
        const errorMsg = row.querySelector('td:nth-child(2)').textContent.trim();
        const stringContent = row.querySelector('.string').textContent.trim();
        const originalText = row.querySelector('.edit-btn').getAttribute('data-original-text');

        if (stringContent === originalText || originalText === null) {
            rows.push({
                'String ID': stringId,
                'lang_tag': langTag,
                'error_msg': errorMsg,
                'content': stringContent
            });
        }
    });

    if (rows.length === 0) {
        alert('沒有可下載的錯誤字串！');
        return;
    }

    generateAndDownloadExcel(rows);
}

function generateAndDownloadExcel(rows) {
    const worksheet = XLSX.utils.json_to_sheet(rows);
    worksheet['!cols'] = [
        { wch: 10 },
        { wch: 10 },
        { wch: 40 },
        { wch: 100 }
    ];

    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, '錯誤字串');

    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
    const blob = new Blob([excelBuffer], { type: 'application/octet-stream' });

    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `error_string.xlsx`;
    link.click();

    URL.revokeObjectURL(link.href);
}