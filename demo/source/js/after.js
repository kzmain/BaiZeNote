//添加/移除class
let toggleClass = function(element, className) {
    if (element.classList.contains(className)) {
        element.classList.remove(className)
    } else {
        element.classList.add(className)
    }
};
//封装document.querySelector
let docGet = function(selector){
    return document.querySelector(selector);
};
//开关目录
let toggleMenu = function(){
    let sectionMenu = docGet('#section-menu')
    let noteMenu = docGet('#note-menu')
    let showNoteArea = docGet('#show-note-area')
    
    //添加/移除 hide，hide存在时隐藏该结点
    toggleClass(noteMenu,'hide')
    toggleClass(sectionMenu,'hide')

    //添加/移除目录的fixed形式
    toggleClass(noteMenu,'section-menu-fixed')
    toggleClass(sectionMenu,'note-menu-fixed')

    //移除/添加所有设置了fixed的col排列
    toggleClass(noteMenu,'col-5')
    toggleClass(noteMenu,'col-sm-5')
    toggleClass(sectionMenu,'col-5')
    toggleClass(sectionMenu,'col-sm-5')

    //添加/移除全屏显示
    toggleClass(showNoteArea,'col-12')
    toggleClass(showNoteArea,'col-sm-12')
    toggleClass(showNoteArea,'col-md-12')
    toggleClass(showNoteArea,'col-lg-12')
    
    toggleCoverShadow()
}
//添加/移除阴影
let toggleCoverShadow = function (){
    let coverShadow = docGet('.cover-shadow')
    if(coverShadow==null){
        //创建阴影节点
        let divnode = document.createElement('div');
        divnode.setAttribute('class','cover-shadow');
        docGet('.row').appendChild(divnode);
        divnode.addEventListener('click',function(){toggleMenu()})
    }
    else{
        docGet('.row').removeChild(coverShadow);
    }
}
//汉堡按钮开关目录
docGet('.button-menu').addEventListener('click',function(){
    toggleMenu()
});
//点击阴影部分也可以开关目录
let coverShadow = docGet('.cover-shadow')
coverShadow.addEventListener('click',function(){
    toggleMenu()

})
//小屏幕下默认关闭目录
let screenWidth = window.screen.width ;
console.log(screenWidth)
if(screenWidth<768){
    toggleMenu()
}
