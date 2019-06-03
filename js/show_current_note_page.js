function show_current_note_page(section_id, md_id) {
    let show_note_area = document.getElementById("show-note-area");
    let show_menu_area = document.getElementById("section-menu");
    let note_path_relative = note_menu_dict[section_id][md_id]["html_path_relative"] + ".note.html";
    let menu_path_relative = note_menu_dict[section_id][md_id]["html_path_relative"] + ".menu.html";
    get_local_file(note_path_relative, show_note_area);
    get_local_file(menu_path_relative, show_menu_area);
}

function get_local_file(file_location, change_tag) {
    let rawFile = new XMLHttpRequest();
    rawFile.onreadystatechange = function () {
        if (rawFile.readyState === 4) {
            if (rawFile.status === 200 || rawFile.status === 0) {
                change_tag.innerHTML = rawFile.responseText;
            }
        }
    };
    rawFile.open("GET", file_location);
    rawFile.send(null);
}