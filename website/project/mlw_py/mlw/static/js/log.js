const searchform = document.getElementById('log-form');
const tableBody = document.querySelectorAll('tbody')[0];
const search_old_log = document.getElementById('search-old-log');
const base_url = get_base_url();

let currentPage = 1;
const itemsPerPage = 50;
let log_data;

initialize()

searchform.addEventListener('submit', function(e) {
    e.preventDefault();

    var formData = new FormData(searchform);
    search_log(formData);
})

search_old_log.addEventListener('click', function(e) {
    e.preventDefault();
    let current_url = window.location.href
    new_url = current_url.replace('mlw', 'multi-language-web');
    window.location.replace(new_url)
})

function initialize() {
    searchform.reset()
    search_log(new FormData(searchform))
}

function search_log(formData) {
    fetch(`/${base_url}/log`, {
        method: 'POST',
        body: formData,
    })
    .then(handle_response_status)
    .then(response => response.json())
    .then(data => {
        log_data = data;
        tableBody.innerHTML = '';
        render_log_table(log_data, true)
    })
    .catch(error => {
        generateModalContent('error', error)
    })
}

function render_log_table(data, first = false) {
    // Sort keys only on the first render
    if (first) {
        sortedKeys = Object.keys(data).map(Number).sort((a, b) => b - a); // 取得鍵並轉為數字，然後反轉
    }

    const totalItems = sortedKeys.length; 
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    currentPage = Math.max(1, Math.min(currentPage, totalPages));

    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, totalItems);
    
    tableBody.innerHTML = '';

    sortedKeys.slice(startIndex, endIndex).forEach(key => {
        const item = data[key];
        const tr = document.createElement("tr");
        tr.classList.add(`table-${getBackgroundColor(item.type)}`);

        ['username', 'type', 'log', 'time'].forEach(field => {
            const td = document.createElement('td');
            td.innerHTML = item[field];
            tr.appendChild(td);
        });

        tableBody.appendChild(tr);
    });

    updatePaginationControls(totalPages);
}

function getBackgroundColor(type) {
    const colors = {
        'Create': 'success',
        'Update': 'warning',
        'Remove': 'danger',
        'New': 'info',
        'Recover': 'secondary',
    };
    return colors[type] || 'default';
}

function updatePaginationControls(totalPages) {
    const paginationContainer = document.getElementById('pagination');
    paginationContainer.innerHTML = '';

    const nav = document.createElement('nav');
    nav.setAttribute('aria-label', 'Page navigation example');
    
    const ul = document.createElement('ul');
    ul.classList.add('pagination', 'justify-content-center');

    // Create pagination buttons
    const createPageButton = (text, onClick, disabled = false) => {
        const li = document.createElement('li');
        if (disabled) {
            li.classList.add('page-item', 'disabled');
        } else {
            li.classList.add('page-item');
        }
        const link = document.createElement('a');
        link.classList.add('page-link');
        link.href = '#';
        link.textContent = text;
        link.onclick = (e) => {
            e.preventDefault();
            if (!disabled) onClick();
        };
        li.appendChild(link);
        return li;
    };

    // Previous button
    ul.appendChild(createPageButton('<', () => {
        if (currentPage > 1) currentPage--;
        render_log_table(log_data);
    }, currentPage === 1));

    // Pagination logic
    const maxPagesToShow = 5; // 最多顯示的頁碼數
    const showEllipses = (start, end) => {
        if (start > 2 || end < 7) ul.appendChild(createPageButton('...', () => {}));
    };

    const startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2));
    const endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);

    // 顯示頁碼
    if (startPage > 1) {
        ul.appendChild(createPageButton(1, () => {
            currentPage = 1;
            render_log_table(log_data);
        }));
        showEllipses(startPage, endPage);
    }

    for (let i = startPage; i <= endPage; i++) {
        ul.appendChild(createPageButton(i, () => {
            currentPage = i;
            render_log_table(log_data);
        }, i === currentPage));
    }

    if (endPage < totalPages) {
        showEllipses(startPage, endPage);
        ul.appendChild(createPageButton(totalPages, () => {
            currentPage = totalPages;
            render_log_table(log_data);
        }));
    }

    // Next button
    ul.appendChild(createPageButton('>', () => {
        if (currentPage < totalPages) currentPage++;
        render_log_table(log_data);
    }, currentPage === totalPages));

    nav.appendChild(ul);
    paginationContainer.appendChild(nav);
}
