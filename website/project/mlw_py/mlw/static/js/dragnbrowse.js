const dragArea = document.querySelector('.drag-area');
const dragText = document.querySelector('.upload-header');
const msgFolder = document.getElementById("messagesfolder");
var progressArea = document.querySelector(".progress-area");
var uploadedArea = document.querySelector(".uploaded-area");


let files_btn = document.getElementById('files_btn');
let files_input = document.getElementById('fileselect');
let folder_btn = document.getElementById('folder_btn');
let folder_input = document.getElementById('folderselect');
let submit_btn = document.getElementsByClassName('btn btn-primary')[1];
let uploadfolder = document.getElementById('uploadfolder');

let files;
var fileCount = 0;
var uploadCount = 0;

// browse files button
files_btn.onclick = () => {
    files_input.click();
}

// browse folder button
folder_btn.onclick = () => {
    folder_input.click();
}


// Handler of select files or folder button
function FileSelectHandler(e) {
    // reset file
    uploadFileNameArray = new Array();
    fileCount = 0;
    uploadCount = 0;

    // empty msg folder and uploaded area
    uploadedArea.innerHTML = "";
    msgFolder.innerHTML = "";

    // fetch FileList object
    files = e.target.files;

    // push filename to name array and upload if chosen file is excel file
    for (let i = 0; i < files.length; i++) {
        if(files[i].type === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") {
            fileCount++;
            uploadFileNameArray.push(files[i].name);
            uploadFile(files[i]);
        }
        else {
            generateModalContent("alert", "只能上傳excel檔案!!")
        }
    }
}

// for drag and drop to traverse directory to get file name
function traverseFileTree(item, path) {
    path = path || "";

    if (item.isFile) {
        // item is file => push to name array and upload
        if(check_isValid(item)) {
            item.file(function (file) {
                uploadFileNameArray.push(file.name);
                fileCount++;
                uploadFile(file)
            });
            return true;
        }
        
        return false;
    }
    else if (item.isDirectory) {
        isValidExcel = true;
        // item is directory new a directory reader to read directory
        var dirReader = item.createReader();
        dirReader.readEntries(function (entries) {
            
            for (var i = 0; i < entries.length; i++) {
                if(check_isValid(entries[i])) {
                    traverseStatus = traverseFileTree(entries[i], path + item.name + "/");
                    if(traverseStatus == false) {
                        isValidExcel = false;
                    }
                }
                else {
                    if(isValidExcel === true) {
                        generateModalContent("alert", "只能上傳excel檔案!!")
                    }
                    isValidExcel = false;
                }
            }
            return isValidExcel;
        });
        
    }
}

// file upload
function uploadFile(file) {
    // upload selected files and show upload progress
    let xhr = new XMLHttpRequest();
    let data = new FormData();

    progressArea.style.display = "block";
    uploadedArea.style.display = "block";

    // add file to formdata
    data.append('file', file);

    xhr.open("POST", "/mlw/upload/" + file.name);

    // listen upload progress and insert html to section progress-area or uploaded-area
    xhr.upload.addEventListener("progress", ({ loaded, total }) => {
        // calculate loaded file and calculate file total size to print in progress file
        let fileLoaded = Math.floor((loaded / total) * 100);
        let fileTotal = Math.floor(total / 1000);
        let fileSize;

        // transfer file size to KB or MB
        (fileTotal < 1024) ? fileSize = fileTotal + " KB" : fileSize = (loaded / (1024 * 1024)).toFixed(2) + " MB";

        // show upload progress
        let progressHTML = `<li class="rows">                       
                                <div class="content">
                                    <i class="fas fa-file-alt"></i>
                                    <div class="details">
                                        <span class="name">${file.name} • Uploading</span>
                                    </div>
                                </div>
                                <span class="percent">${fileLoaded}%</span>
                            </li>`;
        uploadedArea.classList.add("onprogress");
        progressArea.innerHTML = progressHTML;

        // upload finished
        if (loaded == total) {
            progressArea.innerHTML = "";
            progressArea.style.display = "none";
            let uploadedHTML = `<li class="rows">
                                <div class="content upload">
                                    <i class="fas fa-file-alt"></i>
                                    <div class="details">
                                        <span class="name">${file.name} • Uploaded</span>
                                        <span class="size">${fileSize}</span>
                                    </div>
                                </div>
                                <i class="fas fa-check"></i>
                            </li>`;
            // uploadedArea.classList.remove("onprogress");
            uploadedArea.insertAdjacentHTML("afterbegin", uploadedHTML);
        }
    });

    function upload_callback() {
        if (xhr.readyState == 4) {
            try {
                if (xhr.status == 200) {
                    if (xhr.statusText == "OK") {
                        uploadCount++;
                        console.log("progress: " + uploadCount + "/" + fileCount);
                    } else {
                        generateModalContent("error", `${file.name} 上傳失敗!!`);
                    }
                } else {
                    handle_response_status(xhr);
                }
            } catch (error) {
                generateModalContent("error", error);
            }
        }
    }
    xhr.send(data);
    xhr.onreadystatechange = upload_callback;
}

// check is excel file
function check_isValid(item) {
    result = false;

    if(item.isDirectory || item.isFile && item.name.includes(".xlsx")) {
        result = true;
    }
    return result;
}

/**********************
 *    Add listener    *
 **********************/
dragArea.addEventListener('dragover', (event) => {
    event.preventDefault();
    dragText.textContent = 'Release to upload';
    dragArea.classList.add('active');
});

dragArea.addEventListener('dragleave', () => {
    dragText.textContent = 'Drag & Drop';
    dragArea.classList.remove('active');
});

dragArea.addEventListener('drop', (event) => {
    event.preventDefault();
    dragText.textContent = 'Drag & Drop';
    dragArea.classList.remove('active');

    // init data
    uploadFileNameArray = new Array();
    fileCount = 0;
    uploadCount = 0;
    alerted = false;

    // empty msg folder and uploaded area
    uploadedArea.innerHTML = "";
    msgFolder.innerHTML = "";
    // traverse directory to get file
    var items = event.dataTransfer.items;
    
    for (var i = 0; i < items.length; i++) {
        var item = items[i].webkitGetAsEntry();

        // upload excel file
        if (check_isValid(item)) {
            traverseFileTree(item);
        }
        else {
            if(!alerted) {
                generateModalContent("alert", "只能上傳excel檔案!!")
                alerted = true;
            }
            
        }
    }
});

files_input.addEventListener("change", FileSelectHandler);
folder_input.addEventListener("change", FileSelectHandler);