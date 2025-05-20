const selectedPlatform = document.getElementsByName('select_platform_id');
const selectedApp = document.getElementsByName('select_app_id')
const resetBtns = document.getElementsByClassName("btn btn-secondary");
const forms = document.querySelectorAll('form');
const base_url = get_base_url();
initialize()

Array.from(resetBtns).forEach(function(btn) {
    btn.addEventListener('click', function() {
        var applist = this.form.querySelector('form select[name="select_app_id"]')
        initAppList(applist)
    });
});

selectedPlatform.forEach(selectPid => {
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
        
        const formData = new FormData(form);
        var resetBtn = form.querySelector('form button[type="reset"]');
        resetBtn.addEventListener("click", () => {
            applist = form.querySelector('form select[name="select_app_id"]')
            initAppList(applist)
        })

        var downloadType = form.id.split('-')[0];
        if (downloadType == 'svn') {
            if (form[0].value === "-1" || form[1].value === "-1") {
                generateModalContent('alert', '請選擇平台和App')
                return;
            }
        }
        var submitBtn = form.querySelector('form button[type="submit"]');
        formData.append('download_type', downloadType);
        disableBtn(submitBtn)
        exportData(formData, submitBtn);
    });
});

function initialize() {
    forms.forEach(form => {
        form.reset()
    })
}

function exportData(formData, submitBtn) {
    fetch(`/${base_url}/download`, {
        method: 'POST',
        body: formData
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
        if (formData.get("download_type") == 'svn') {
            a.download = 'svn_files.zip';
        }
        else {
            a.download = 'excel_files.zip'; // Set the file name
        }
        document.body.appendChild(a); // Append to the body
        a.click(); // Programmatically click the link to trigger the download
        a.remove(); // Remove the link from the document
        window.URL.revokeObjectURL(url); // Clean up the URL object
    })
    .catch(error => {
        generateModalContent('error', error)
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerText = "下載";
    });
}