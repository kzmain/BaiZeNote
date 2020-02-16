    let current_section_id = "";
    let current_note_id = "";
    let note_history_dict = {};


    //显示笔记
    function read_note_text(section_id, note_id) {
        let show_note_area = document.getElementById("show-note-area");
        get_notes_html(show_note_area, section_id, note_id);
    }

    function get_note_menu(section_id, note_id = -1) {
        if (current_section_id === parseInt(section_id)) {
            return
        }
        // read_note_text(section_id, note_id);
        if (current_section_id !== "") {
            document.getElementById("section-span-" + current_section_id).classList.remove("active");
        }
        let section_element = document.getElementById("section-span-" + section_id);
        section_element.classList.add("active");
        let section_name = section_element.innerText.trim();
        let title_element = document.getElementById("title");
        let og_title = document.getElementById("og-title");
        title_element.innerText = section_name + " - " + notebook_name;
        og_title.content = section_name + " - " + notebook_name;
        current_section_id = section_id;

        let note_menu = document.getElementById("note-menu");
        // 删除 note_menu 原先所有显示note_list
        while (note_menu.firstChild) {
            note_menu.removeChild(note_menu.firstChild)
        }
        // 获取现在 section 所有笔记情况
        let section_files_info = note_menu_dict[section_id];
        // 如果 没有note 直接 显示没有笔记 并返回
        if (Object.keys(section_files_info).length === 0) {
            let show_note_area = document.getElementById("show-note-area");
            show_note_area.innerHTML = "<h1>" + section_name + " section is empty" + "</h1>";
            return
        }
        for (let file_id in section_files_info) {
            let note_span = document.createElement('span');
            if (section_files_info.hasOwnProperty(file_id)) {
                note_span.innerText = section_files_info[file_id]["NOTE_FILE_NAME"];
                note_span.setAttribute("onclick", "get_note('" + section_id + "','" + file_id + "');noteMenuAutoToggle();");
                note_menu.appendChild(note_span);
                note_span.setAttribute("id", section_id + "-" + file_id);
            }
        }


        if (note_id === -1) {
            //如果历史上 曾点过词section，获取最后一次访问的 note-id 标记为 active 并且显示对应的 note 内容
            if (!note_history_dict.hasOwnProperty(section_id)) {
                note_history_dict[section_id] = Object.keys(note_menu_dict[section_id])[0];
            }
            note_id = note_history_dict[section_id];
        }

        let note_element = document.getElementById(section_id + "-" + note_id);
        let note_name = note_element.innerText.trim();
        title_element.innerText = section_name + " - " + note_name + " - " + notebook_name;

        current_note_id = note_id;
        get_note(section_id, note_id)
    }

    function get_note(section_id, note_id) {
        let section_element = document.getElementById("section-span-" + section_id);
        let note_element = document.getElementById(section_id + "-" + note_id);
        let title_element = document.getElementById("title");
        let og_title = document.getElementById("og-title");
        let note_name = note_element.innerText.trim();
        let section_name = section_element.innerText.trim();
        title_element.innerText = section_name + " - " + note_name + " - " + notebook_name;
        og_title.content = section_name + " - " + note_name + " - " + notebook_name;

        read_note_text(section_id, note_id);
        // Remove active class note span in note menu
        // 去除现在note menu所有 active 的 class 的 note
        document.getElementById(current_section_id + "-" + current_note_id).classList.remove("active");
        document.getElementById(section_id + "-" + note_id).classList.add("active");
        current_section_id = section_id;
        current_note_id = note_id;
        note_history_dict[current_section_id] = current_note_id
    }

    function get_notes_html(change_tag, section_id, note_id) {
        change_tag.innerHTML = note_menu_dict[section_id][note_id]["HTML"];
    }

    function expand_note_menu(section_id) {
        let current_section_span = document.getElementById("section-span-" + section_id).parentElement;
        while (current_section_span.id !== "section-menu") {
            current_section_span.classList.add("show");
            current_section_span = current_section_span.parentElement
        }

    }