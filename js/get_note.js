function readTextFile(section_id, note_id) {
    let show_note_area = document.getElementById("show-note-area");
    // show_note_area.innerHTML = note_menu_dict[section_id][note_id]["html_path_relative"]
    let file_location = note_menu_dict[section_id][note_id]["html_path_relative"] + ".note.html"
    let rawFile = new XMLHttpRequest();
    rawFile.onreadystatechange = function () {
        if (rawFile.readyState === 4) {
            if (rawFile.status === 200 || rawFile.status === 0) {
                show_note_area.innerHTML = rawFile.responseText;
            }
        }
    }
    rawFile.open("GET", file_location);
    rawFile.send(null);
}