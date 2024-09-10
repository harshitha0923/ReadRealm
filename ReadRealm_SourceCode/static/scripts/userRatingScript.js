function getBookID() {
    var bookurl = window.location.href;
    var bookId = bookurl.split("/");
    return bookId[bookId.length - 1];
}
let userPriorStars = document.currentScript.getAttribute('default-value');
var stars =  document.querySelectorAll(".stars i");
// Dedault Star Rating
for(let i=0;i<userPriorStars;i++){
    stars[i].classList.add("active");
}
if(userPriorStars == 0){
    for(let i=0;i<userPriorStars;i++){
        stars[i].classList.remove("active");
    }
}
let finalindex;
stars.forEach((star, index1)=>{
    star.addEventListener("click", () => {
        updateRatings(index1);
        stars.forEach((star, index2)=>{
            index1 >= index2 ? star.classList.add("active") : star.classList.remove("active");
        });
    });
});

function updateRatings(value){
    // Added 1 to adjust for index
    let requestData = JSON.stringify({id : getBookID(), userRate: value+1});
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", "/updateuserrating");
    xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xmlhttp.send(requestData);
    xmlhttp.onreadystatechange = () => {
        if (xmlhttp.readyState == XMLHttpRequest.DONE && xmlhttp.status == 200) {
            var dataFromServer = JSON.parse(xmlhttp.response);
            console.log(dataFromServer.message.message)
        }
    }
}