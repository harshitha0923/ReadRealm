window.onload = getReviewComments();        
function getBookID() {
    var bookurl = window.location.href;
    var bookId = bookurl.split("/");
    return bookId[bookId.length - 1];
}

function wantread() {
    var requestData = JSON.stringify({ id: getBookID() });
    var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
    xmlhttp.open("POST", "/wantread");
    xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xmlhttp.send(requestData);
    xmlhttp.onreadystatechange = () => {
        if (xmlhttp.readyState == XMLHttpRequest.DONE && xmlhttp.status == 200) {
            var dataFromServer = JSON.parse(xmlhttp.response);
            console.log(dataFromServer.message.message)
        }
    }
}

function readit() {
    var requestData = JSON.stringify({ id: getBookID() });
    var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
    xmlhttp.open("POST", "/readit");
    xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xmlhttp.send(requestData);
    xmlhttp.onreadystatechange = () => {
        if (xmlhttp.readyState == XMLHttpRequest.DONE && xmlhttp.status == 200) {
            var dataFromServer = JSON.parse(xmlhttp.response);
            console.log(dataFromServer.message.message)
        }
    }
}

function currentread() {
    var requestData = JSON.stringify({ id: getBookID() });
    var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
    xmlhttp.open("POST", "/currentread");
    xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xmlhttp.send(requestData);
    xmlhttp.onreadystatechange = () => {
        if (xmlhttp.readyState == XMLHttpRequest.DONE && xmlhttp.status == 200) {
            var dataFromServer = JSON.parse(xmlhttp.response);
            console.log(dataFromServer.message.message)
        }
    }
}


function getReviewComments() {
var requestData = JSON.stringify({ id: getBookID() });
var xmlhttp = new XMLHttpRequest();
xmlhttp.open("POST", "/reviewsContent", true);
xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
xmlhttp.send(requestData);
xmlhttp.onreadystatechange = function () {
if (xmlhttp.readyState === 4 && xmlhttp.status === 200) {
    var response = JSON.parse(xmlhttp.responseText);
    onLoadStarRating();
    if (response.dataReviews && response.dataReviews.comments) {
        createTable(response.dataReviews.comments);
    } else {
        console.log('No reviews received or dataReviews is missing');
        }
    }
    }
}



function createTable(comments) {
var reviewContainer = document.getElementById("reviewContainer");
if (!reviewContainer) {
console.log("Review container not found");
return;
}
reviewContainer.innerHTML = ''; // Clear previous entries

var table = document.createElement('table');
table.className = 'table table-striped';
var tbody = document.createElement('tbody');

comments.forEach(function(comment) {
var tr = document.createElement('tr');
var td = document.createElement('td');
td.textContent = comment;
tr.appendChild(td);
tbody.appendChild(tr);
});

table.appendChild(tbody);
reviewContainer.appendChild(table);
}

function addComment() {
var addCommentValue = document.getElementById('addCommentInput').value;
    if (addCommentValue.length > 0) {
        var bookidVal = getBookID();
        var sendData = { bookid: bookidVal, newComment: addCommentValue };
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("POST", "/addComment");
        xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xmlhttp.send(JSON.stringify(sendData));
        xmlhttp, onreadystatechange = () => {
            if (xmlhttp.readyState == XMLHttpRequest.DONE && xmlhttp.status == 200) {
                window.location.reload(true);
            }
        };
        window.location.reload(true);
    }
}

function onLoadStarRating(){

    let getStarDiv = document.getElementById("rating1");
    let value = parseFloat(getStarDiv.getAttribute("data-value"));
    if(value ==0){
        for (let i=0;i<5;i++){
            let starCreate = document.createElement("i");
            starCreate.classList.add("fa","fa-star", "averageRating2");
            getStarDiv.appendChild(starCreate);
        }
    }else{
    let val = Math.round(value*2)/2;
    let fractional = Math.abs(val) - Math.floor(val);
    let whole = Math.floor(val);
    for (let i=0;i<whole;i++){
        let starCreate = document.createElement("i");
        starCreate.classList.add("fa-solid","fa-star", "averageRating");
        getStarDiv.appendChild(starCreate);
    }
    if(fractional>0){
        let starCreate = document.createElement("i");
        starCreate.classList.add("fa-solid", "fa-star-half-stroke", "averageRating");
        getStarDiv.appendChild(starCreate);

    }
    val = 5 - val;
    fractional = Math.abs(val) - Math.floor(val);
    whole = Math.floor(val);
    for (let i=0;i<whole;i++){
        let starCreate = document.createElement("i");
        starCreate.classList.add("fa","fa-star", "averageRating2");
        getStarDiv.appendChild(starCreate);
    }
    }
}



