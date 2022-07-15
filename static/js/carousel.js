const label = document.getElementsByClassName('TagName');
const carousel_item = document.getElementsByClassName('carousel-item');


let changeCarousel = () =>{
    for (let i=0; i<carousel_item.length; i++){
    if(carousel_item[i].classList.contains('active')){
        label[i].removeAttribute('hidden')
    }
}
}