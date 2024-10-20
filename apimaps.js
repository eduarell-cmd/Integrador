function getlocation(){
    if(navigator.geolocation){
        navigator.geolocation.getCurrentPosition(showPosition,showError);
    }
}

function showPosition(position){
    document.querySelector('.myForm input[name= "latitude').v
}