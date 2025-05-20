newLangFrom = document.getElementById('new-lang-form')
modifyLangFrom = document.getElementById('modify-lang-form')
newLangTag = document.getElementsByName('new-lang-tag')[0]
newLangEN = document.getElementsByName('new-lang-en')[0]
newLangZH = document.getElementsByName('new-lang-zh')[0]
modifyLangTag = document.getElementsByName('modify-lang-tag')[0]
modifyLangEN = document.getElementsByName('modify-lang-en')[0]
modifyLangZH = document.getElementsByName('modify-lang-zh')[0]
tagDiv = document.getElementById('tag-div')
enDiv = document.getElementById('en-div')
zhDiv = document.getElementById('zh-div')
langSelect = document.getElementById('language-select');
const base_url = get_base_url();
initialize()

langSelect.addEventListener('change', (e) => {
    e.preventDefault();

    lang_id = langSelect.value;

    fetch(`/${base_url}/language/${lang_id}`, {
        method: 'GET',
    })
    .then(handle_response_status)
    .then(function (response) {
        return response.json();
    })
    .then(function (data) {
        modifyLangTag.value = data['tag'];
        modifyLangEN.value = data['en'];
        modifyLangZH.value = data['zh'];

        tagDiv.style.display = 'block';
        enDiv.style.display = 'block';
        zhDiv.style.display = 'block';
    })
    .catch(error => {
        generateModalContent('error', error)
    })
})

modifyLangFrom.addEventListener('submit', (e) => {
    e.preventDefault();
    lang_id = langSelect.value;

    if(lang_id == -1) {
        generateModalContent("alert", "請選擇語言!!")
        return false;
    }

    data = {}
    data['lang_id'] = lang_id;
    data['tag'] = (modifyLangTag.value).trim();
    data['en'] = (modifyLangEN.value).trim();
    data['zh'] = (modifyLangZH.value).trim();

    fetch(`/${base_url}/language/${lang_id}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(handle_response_status)
    .then(function (response) {
        return response.json();
    })
    .then(function (data) {
        if(data['msg'] === 'success') {
            generateModalContent("alert", "修改語言成功!!")
            document.forms['modify-lang-form'].reset();
        }
        else{
            generateModalContent("error", "修改失敗!!\nerror msg: " + data['msg'])
        }
    })
    .catch(error => {
        generateModalContent('error', error)
    })
})

newLangFrom.addEventListener('submit', (e) => {
    e.preventDefault();
    data = {}
    data['tag'] = (newLangTag.value).trim();
    data['en'] = (newLangEN.value).trim();
    data['zh'] = (newLangZH.value).trim();

    fetch(`/${base_url}/language`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(handle_response_status)
    .then(function (response) {
        return response.json();
    })
    .then(function (data) {
        if(data['msg'] === 'success') {
            generateModalContent("alert", "新增語言成功!!")
            document.forms['new-lang-form'].reset();
        }
        else{
            generateModalContent("error", "新增失敗!!\nerror msg: " + data['msg'])
        }
    })
    .catch(error => {
        generateModalContent('error', error)
    })
})

function initialize() {
    document.forms['new-lang-form'].reset();
    document.forms['modify-lang-form'].reset();

    tagDiv.style.display = 'none';
    enDiv.style.display = 'none';
    zhDiv.style.display = 'none';
}