/**
 * Template Name: NiceAdmin
 * Template URL: https://bootstrapmade.com/nice-admin-bootstrap-admin-html-template/
 * Updated: Apr 20 2024 with Bootstrap v5.3.3
 * Author: BootstrapMade.com
 * License: https://bootstrapmade.com/license/
 */

(function () {
	"use strict";

	/**
	 * Easy selector helper function
	 */
	const select = (el, all = false) => {
		el = el.trim();
		if (all) {
			return [...document.querySelectorAll(el)];
		} else {
			return document.querySelector(el);
		}
	};

	/**
	 * Easy event listener function
	 */
	const on = (type, el, listener, all = false) => {
		if (all) {
			select(el, all).forEach((e) => e.addEventListener(type, listener));
		} else {
			select(el, all).addEventListener(type, listener);
		}
	};

	/**
	 * Easy on scroll event listener
	 */
	const onscroll = (el, listener) => {
		el.addEventListener("scroll", listener);
	};

	/**
	 * Sidebar toggle
	 */
	if (select(".toggle-sidebar-btn")) {
		on("click", ".toggle-sidebar-btn", function (e) {
			select("body").classList.toggle("toggle-sidebar");
		});
	}

	/**
	 * Navbar links active state on scroll
	 */
	let navbarlinks = select("#navbar .scrollto", true);
	const navbarlinksActive = () => {
		let position = window.scrollY + 200;
		navbarlinks.forEach((navbarlink) => {
			if (!navbarlink.hash) return;
			let section = select(navbarlink.hash);
			if (!section) return;
			if (
				position >= section.offsetTop &&
				position <= section.offsetTop + section.offsetHeight
			) {
				navbarlink.classList.add("active");
			} else {
				navbarlink.classList.remove("active");
			}
		});
	};
	window.addEventListener("load", navbarlinksActive);
	onscroll(document, navbarlinksActive);

	/**
	 * Toggle .header-scrolled class to #header when page is scrolled
	 */
	let selectHeader = select("#header");
	if (selectHeader) {
		const headerScrolled = () => {
			if (window.scrollY > 100) {
				selectHeader.classList.add("header-scrolled");
			} else {
				selectHeader.classList.remove("header-scrolled");
			}
		};
		window.addEventListener("load", headerScrolled);
		onscroll(document, headerScrolled);
	}

	/**
	 * Back to top button
	 */
	let backtotop = select(".back-to-top");
	if (backtotop) {
		const toggleBacktotop = () => {
			if (window.scrollY > 100) {
				backtotop.classList.add("active");
			} else {
				backtotop.classList.remove("active");
			}
		};
		window.addEventListener("load", toggleBacktotop);
		onscroll(document, toggleBacktotop);
	}

	/**
	 * Initiate tooltips
	 */
	var tooltipTriggerList = [].slice.call(
		document.querySelectorAll('[data-bs-toggle="tooltip"]')
	);
	var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
		return new bootstrap.Tooltip(tooltipTriggerEl);
	});

	/**
	 * Initiate quill editors
	 */
	if (select(".quill-editor-default")) {
		new Quill(".quill-editor-default", {
			theme: "snow",
		});
	}

	if (select(".quill-editor-bubble")) {
		new Quill(".quill-editor-bubble", {
			theme: "bubble",
		});
	}

	if (select(".quill-editor-full")) {
		new Quill(".quill-editor-full", {
			modules: {
				toolbar: [
					[
						{
							font: [],
						},
						{
							size: [],
						},
					],
					["bold", "italic", "underline", "strike"],
					[
						{
							color: [],
						},
						{
							background: [],
						},
					],
					[
						{
							script: "super",
						},
						{
							script: "sub",
						},
					],
					[
						{
							list: "ordered",
						},
						{
							list: "bullet",
						},
						{
							indent: "-1",
						},
						{
							indent: "+1",
						},
					],
					[
						"direction",
						{
							align: [],
						},
					],
					["link", "image", "video"],
					["clean"],
				],
			},
			theme: "snow",
		});
	}

	/**
	 * Initiate TinyMCE Editor
	 */

	const useDarkMode = window.matchMedia("(prefers-color-scheme: dark)").matches;
	const isSmallScreen = window.matchMedia("(max-width: 1023.5px)").matches;

	tinymce.init({
		selector: "textarea.tinymce-editor",
		plugins:
			"preview importcss searchreplace autolink autosave save directionality code visualblocks visualchars fullscreen image link media codesample table charmap pagebreak nonbreaking anchor insertdatetime advlist lists wordcount help charmap quickbars emoticons accordion",
		editimage_cors_hosts: ["picsum.photos"],
		menubar: "file edit view insert format tools table help",
		toolbar:
			"undo redo | accordion accordionremove | blocks fontfamily fontsize | bold italic underline strikethrough | align numlist bullist | link image | table media | lineheight outdent indent| forecolor backcolor removeformat | charmap emoticons | code fullscreen preview | save print | pagebreak anchor codesample | ltr rtl",
		autosave_ask_before_unload: true,
		autosave_interval: "30s",
		autosave_prefix: "{path}{query}-{id}-",
		autosave_restore_when_empty: false,
		autosave_retention: "2m",
		image_advtab: true,
		link_list: [
			{
				title: "My page 1",
				value: "https://www.tiny.cloud",
			},
			{
				title: "My page 2",
				value: "http://www.moxiecode.com",
			},
		],
		image_list: [
			{
				title: "My page 1",
				value: "https://www.tiny.cloud",
			},
			{
				title: "My page 2",
				value: "http://www.moxiecode.com",
			},
		],
		image_class_list: [
			{
				title: "None",
				value: "",
			},
			{
				title: "Some class",
				value: "class-name",
			},
		],
		importcss_append: true,
		file_picker_callback: (callback, value, meta) => {
			/* Provide file and text for the link dialog */
			if (meta.filetype === "file") {
				callback("https://www.google.com/logos/google.jpg", {
					text: "My text",
				});
			}

			/* Provide image and alt text for the image dialog */
			if (meta.filetype === "image") {
				callback("https://www.google.com/logos/google.jpg", {
					alt: "My alt text",
				});
			}

			/* Provide alternative source and posted for the media dialog */
			if (meta.filetype === "media") {
				callback("movie.mp4", {
					source2: "alt.ogg",
					poster: "https://www.google.com/logos/google.jpg",
				});
			}
		},
		height: 600,
		image_caption: true,
		quickbars_selection_toolbar:
			"bold italic | quicklink h2 h3 blockquote quickimage quicktable",
		noneditable_class: "mceNonEditable",
		toolbar_mode: "sliding",
		contextmenu: "link image table",
		skin: useDarkMode ? "oxide-dark" : "oxide",
		content_css: useDarkMode ? "dark" : "default",
		content_style:
			"body { font-family:Helvetica,Arial,sans-serif; font-size:16px }",
	});

	/**
	 * Initiate Bootstrap validation check
	 */
	var needsValidation = document.querySelectorAll(".needs-validation");

	Array.prototype.slice.call(needsValidation).forEach(function (form) {
		form.addEventListener(
			"submit",
			function (event) {
				if (!form.checkValidity()) {
					event.preventDefault();
					event.stopPropagation();
				}

				form.classList.add("was-validated");
			},
			false
		);
	});

	/**
	 * Initiate Datatables
	 */
	const datatables = select(".datatable", true);
	datatables.forEach((datatable) => {
		new simpleDatatables.DataTable(datatable, {
			perPageSelect: [5, 10, 15, ["All", -1]],
			columns: [
				{
					select: 2,
					sortSequence: ["desc", "asc"],
				},
				{
					select: 3,
					sortSequence: ["desc"],
				},
				{
					select: 4,
					cellClass: "green",
					headerClass: "red",
				},
			],
		});
	});

	/**
	 * Autoresize echart charts
	 */
	const mainContainer = select("#main");
	if (mainContainer) {
		setTimeout(() => {
			new ResizeObserver(function () {
				select(".echart", true).forEach((getEchart) => {
					echarts.getInstanceByDom(getEchart).resize();
				});
			}).observe(mainContainer);
		}, 200);
	}
})();





function get_base_url() {
	var base_url = window.location.pathname.split( '/' )[1];
	return base_url;
}

function get_apps(platform_id) {
	return fetch("/mlw/apps/" + platform_id, {
		method: "GET",
	});
}

function check_platform_and_app_select(platform_id, app_id) {
	if (platform_id === "-1" || app_id === "-1") {
		generateModalContent('alert', '請選擇平台與App')
		return false;
	}
	return true;
}

function disableBtn(submitBtn) {
	submitBtn.disabled = true;
	let span = document.createElement("span");
	span.className = "spinner-border spinner-border-sm";
	span.role = "status";
	span.ariaHidden = true;
	submitBtn.appendChild(span);
}

function generateModalContent(type, data, proofread_id) {
    var modalTitle = document.getElementsByClassName('modal-title')[0];
    var modalBody = document.getElementsByClassName('modal-body')[0];
	var downloadBtn = document.getElementById('downloadBtn');
	var removeBtn = document.getElementById('modalRemoveBtn');
	var insertProjectBtn = document.getElementById('insertProjectBtn');
	var modalFooter = document.getElementsByClassName('modal-footer')[0];

	const modalType = {
		'alert': '系統提示',
		'diff': '字串版本差異',
		'error': '錯誤提示',
		'd_search': '下載',
		'remove': '移除',
		'new_project': '新增專案',
	}

	modalTitle.textContent = modalType[type];
	removeBtns(modalFooter, downloadBtn, removeBtn, insertProjectBtn);
	if (type === 'diff') {
		modalBody.innerHTML = createDiffTable(data);
		$('#myModal')[0].firstElementChild.classList.add('modal-xl');
	}
	else if (type === 'd_search') {
		modalBody.innerHTML = data;
		const downloadBtn = create_modal_button('downloadBtn', 'btn btn-dark', '下載')
		downloadBtn.onclick = function() {
			downloadExcel();
		};

		modalFooter.insertBefore(downloadBtn, modalFooter.firstChild);
		$('#myModal')[0].firstElementChild.classList.remove('modal-xl');
	}
	else if (type == 'remove') {
		modalBody.innerHTML = data;
		const removeBtn = create_modal_button('modalRemoveBtn', 'btn btn-dark', '移除');
		removeBtn.onclick = function() {
			if (!proofread_id) {
				let asn_id = document.getElementById('remove-namespace').value;
				removeString(asn_id);
			}
			else {
				remove_project(proofread_id);
			}
		};

		modalFooter.insertBefore(removeBtn, modalFooter.firstChild);
		$('#myModal')[0].firstElementChild.classList.remove('modal-xl');
	}
	else if (type =='new_project') {
		modalBody.innerHTML = data;
		const insertProjectBtn = create_modal_button('insertProjectBtn', 'btn btn-dark', '新增');
		insertProjectBtn.onclick = function() {
			var project_name = document.getElementsByName('project-name')[0].value;
			var spec_link = document.getElementsByName('spec-link')[0].value;
			new_project(project_name, spec_link);
		};

		modalFooter.insertBefore(insertProjectBtn, modalFooter.firstChild);
		$('#myModal')[0].firstElementChild.classList.remove('modal-xl');
	}
	else {
		modalBody.innerHTML = data;
		$('#myModal')[0].firstElementChild.classList.remove('modal-xl');
	}

	$('#myModal').modal('show');
}

function create_modal_button(id, class_name, textcontent) {
	const button = document.createElement('button');
	button.id = id;
	button.className = class_name;
	button.textContent = textcontent;

	return button;
}

function removeBtns(modalFooter, downloadBtn, removeBtn, insertProjectBtn) {
	if (downloadBtn) {
		modalFooter.removeChild(modalFooter.firstChild);
	}
	if (removeBtn) {
		modalFooter.removeChild(modalFooter.firstChild);
	}
	if (insertProjectBtn) {
		modalFooter.removeChild(modalFooter.firstChild);
	}
}

function initAppList(selectApp) {
	while (selectApp.options.length > 1) {
		selectApp.remove(1);
	}

	selectApp.selectedIndex = 0;
}

function sortAppList(data) {
	return Object.keys(data).sort((a, b) => data[a].localeCompare(data[b]));
}

function handle_response_status(response) {
    const res = response.status;
	console.log(res);
    switch(res) {
        case 400:
            throw new Error('無效的操作!');
        case 403:
            throw new Error('目前使用者無使用權限，請先跟管理員申請權限!');
        case 404:
            throw new Error('找不到資料!');
        case 405:
            throw new Error('此功能目前無法使用!');
		case 413:
			generateModalContent('alert', '檔案太大，請分割檔案上傳，或是請管理員增加上限!')
        case 500:
            throw new Error('系統錯誤!請稍後再試，若問題持續發生請通知管理員!');
        case 503: {
            let seconds = 10;
            const countdownInterval = setInterval(() => {
                if (seconds > 0) {
                    generateModalContent('alert', `系統正在維護中! ${seconds} 秒後將自動登出...`);
                } else {
                    clearInterval(countdownInterval);
                    window.location.href = `/${base_url}/logout`;
                }
                seconds--;
            }, 1000);
            return 0;
        }
        default:
            return response;
    }
}

function set_test_mode() {
	testMode = document.getElementById('testModeToggle').checked ? true : false;

	fetch(`/mlw/set_test_mode`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ test_mode: testMode })
	})
	.then(handle_response_status)
	.then(response => response.json())
	.then(data => {
		location.reload();
	})
	.catch(error => {
		generateModalContent('error', error.message);
	});
}
