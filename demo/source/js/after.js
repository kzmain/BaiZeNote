// -----------
let toggleClass = function(element, className) {
    if (element.classList.contains(className)) {
        element.classList.remove(className)
    } else {
        element.classList.add(className)
    }
};

let docGet = function(selector){
    return document.querySelector(selector);
};

let recurToggleClass = function(element,className){
    toggleClass(element,className);
    let child = element.childNodes;
    if (child.length != 0){
        child.forEach(e => {
            if(e.nodeName != "#text"){
                recurToggleClass(e,className)
            }
        });
    }
};
let toggleMenu = function(){
    let sectionMenu = docGet('#section-menu')
    let noteMenu = docGet('#note-menu')
    let showNoteArea = docGet('#show-note-area')
    toggleClass(noteMenu,'hide')
    toggleClass(sectionMenu,'hide')
    //设置为fixed形式
    toggleClass(noteMenu,'section-menu-fixed')
    toggleClass(sectionMenu,'note-menu-fixed')
    //取消/添加所有设置了fixed的col的class
    //col-
    toggleClass(noteMenu,'col-5')
    toggleClass(noteMenu,'col-sm-5')
    toggleClass(sectionMenu,'col-5')
    toggleClass(sectionMenu,'col-sm-5')

    //取消/添加全屏显示
    toggleClass(showNoteArea,'col-12')
    toggleClass(showNoteArea,'col-sm-12')
    toggleClass(showNoteArea,'col-md-12')
    toggleClass(showNoteArea,'col-lg-12')

    toggleCoverShadow()
}
let toggleCoverShadow = function (){
    let coverShadow = docGet('.cover-shadow')
    if(coverShadow==null){
        let divnode = document.createElement('div');
        divnode.setAttribute('class','cover-shadow');
        docGet('.row').appendChild(divnode);
        divnode.addEventListener('click',function(){toggleMenu()})
    }
    else{
        docGet('.row').removeChild(coverShadow);
    }
}

docGet('.button-menu').addEventListener('click',function(){
    toggleMenu()
});
let coverShadow = docGet('.cover-shadow')
coverShadow.addEventListener('click',function(){
    toggleMenu()

})

