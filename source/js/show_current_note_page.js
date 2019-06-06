let current_section_id = "";
let current_note_id = "";
let note_history_dict = {};

function get_note_menu(section_id) {
    let note_menu = document.getElementById("note-menu");
    while (note_menu.firstChild) {
        note_menu.removeChild(note_menu.firstChild)
    }
    let section_files_info = note_menu_dict[section_id];
    for (let md_id in section_files_info) {
        let note_span = document.createElement('span');
        note_span.innerText = section_files_info[md_id]["html_name"];
        let note_id = section_id + "-" + md_id;
        note_span.setAttribute("onclick", "readTextFile('" + section_id + "','" + md_id + "');");
        note_span.setAttribute("id", section_id + "-" + md_id);
        if (note_id === current_note_id) {
            note_span.setAttribute("class", "active");
        }
        note_menu.appendChild(note_span)
    }
    if (note_history_dict.hasOwnProperty(section_id)){
        document.getElementById(section_id + "-" + note_history_dict[section_id]).classList.add("active");
        let new_note_key = note_history_dict[section_id];
        readTextFile(section_id, new_note_key);
    }else if(Object.keys(note_menu_dict[section_id]).length > 0){
        let new_note_key = Object.keys(note_menu_dict[section_id])[0];
        readTextFile(section_id, new_note_key);
    }else{
        let section_name = document.getElementById("section-span-" + section_id.replace("section", "")).innerText.trim();
        let show_note_area = document.getElementById("show-note-area");
        show_note_area.innerHTML = "<h1>" + section_name + " section is empty" + "</h1>"
    }
    // Remove active class note span in note menu
    // 去除现在note menu所有 active 的 class 的 note
    let section_menu = document.getElementById("section-menu");
    let active_sections = section_menu.getElementsByClassName("active");
    for(let i = 0; i < active_sections.length; i++){
        active_sections[i].classList.remove("active")
    }
    // Add active class for clicked note span in note menu
    // note menu中按下的 note 变为 active 的 class
    let click_section_span_id = "section-span-" + section_id.replace("section", "") ;
    let active_note = document.getElementById(click_section_span_id);
    active_note.classList.add("active");
}

function readTextFile(section_id, note_id) {
    let show_note_area = document.getElementById("show-note-area");
    // Remove active class note span in note menu
    // 去除现在note menu所有 active 的 class 的 note
    let note_menu = document.getElementById("note-menu");
    let active_notes = note_menu.getElementsByClassName("active");
    for(let i = 0; i < active_notes.length; i++){
        active_notes[i].classList.remove("active")
    }
    // Add active class for clicked note span in note menu
    // note menu中按下的 note 变为 active 的 class
    let click_span_id = section_id + "-" + note_id;
    let active_note = document.getElementById(click_span_id);
    active_note.classList.add("active");
    // Remember current note_id and section_id
    current_note_id = click_span_id;
    current_section_id = section_id;
    // Read real note from local
    // 从本地读取note内容
    if(note_mode==="server"){
        let file_location = note_menu_dict[section_id][note_id]["html_path_relative"] + ".note.html";
        let rawFile = new XMLHttpRequest();
        rawFile.onreadystatechange = function () {
            if (rawFile.readyState === 4) {
                if (rawFile.status === 200 || rawFile.status === 0) {
                    show_note_area.innerHTML = rawFile.responseText;
                    window.history.pushState(rawFile.responseText, 'Title', note_menu_dict[section_id][note_id]["html_path_relative"]);
                }
            }
        };
        rawFile.open("GET", file_location);
        rawFile.send(null);
    }else if(note_mode==="local"){
        show_note_area.innerHTML = note_menu_dict[section_id][note_id]["html_code"]
    }else{
        console.error("wrong mode")
    }


    // Remember history section_id <-> note_id
    // 记录历史 section_id <-> note_id
    note_history_dict[section_id] = note_id
}

// Only used in "-server" mode
// 只在 "-server" 模式中使用
function show_current_note_page(section_id, note_id) {
    current_section_id = section_id;
    current_note_id = note_id;
    let section_menu_area = document.getElementById("section-menu");
    let section_menu_path_relative = "/source/section-menu.blade.html";
    get_local_file(section_menu_path_relative, section_menu_area, section_id, note_id);
    let show_note_area = document.getElementById("show-note-area");
    let note_path_relative = note_menu_dict[section_id][note_id]["html_path_relative"] + ".note.html";
    get_local_file(note_path_relative, show_note_area, section_id, note_id);
}

// Only used in "-server" mode
// 只在 "-server" 模式中使用
function get_local_file(file_location, change_tag, section_id, note_id) {
    let target_file = new XMLHttpRequest();
    target_file.onreadystatechange = function () {
        if (target_file.readyState === 4) {
            if (target_file.status === 200 || target_file.status === 0) {
                change_tag.innerHTML = target_file.responseText;
                if (file_location === "/source/section-menu.blade.html"){
                    get_note_menu(section_id);
                    readTextFile(section_id, note_id);
                }

            }
        }
    };
    target_file.open("GET", file_location);
    target_file.send(null);
}

