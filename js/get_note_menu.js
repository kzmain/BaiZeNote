function get_note_menu(section_id) {
    let note_menu = document.getElementById("note-menu");
    while (note_menu.firstChild) {
        note_menu.removeChild(note_menu.firstChild)
    }
    let section_files_info = note_menu_dict[section_id];
    for (let key in section_files_info) {
        let note_span = document.createElement('span');
        note_span.innerText = section_files_info[key]["html_name"]
        note_span.setAttribute("onclick", "readTextFile('" + section_id + "','" + key + "');");
        note_menu.appendChild(note_span)
    }
}