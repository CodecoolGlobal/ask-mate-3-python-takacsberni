// you receive an array of objects which you must sort in the by the key "sortField" in the "sortDirection"
function getSortedItems(items, sortField, sortDirection) {
    console.log(items)
    console.log(sortField)
    console.log(sortDirection)

    // === SAMPLE CODE ===
    // if you have not changed the original html uncomment the code below to have an idea of the
    // effect this function has on the table
    //
    if (sortDirection === "asc") {
        for (let i=0; i<items.length; i++) {
            const firstItem = items.shift()
            if (firstItem) {
                items.push(firstItem)
            }
        }
    }
    else {
        for (let i=0; i<items.length; i++) {
            const lastItem = items.pop()
            if (lastItem) {
                items.push(lastItem)
            }
        }
    }

    return items
}

// you receive an array of objects which you must filter by all it's keys to have a value matching "filterValue"
function getFilteredItems(items, filterValue) {
    console.log(items)
    console.log(filterValue)
    let result = []
    // === SAMPLE CODE ===
    // if you have not changed the original html uncomment the code below to have an idea of the
    // effect this function has on the table
    //
    for (let i=0; i<items.length; i++) {
        if (filterValue[0] === "!") {
            if (filterValue.substring(1, 13) === "Description:") {
                if (!(items[i]['Description'].includes(filterValue.substring(13, filterValue.length)))) {
                    result.push(items[i])
                }
            }
            else if (!(items[i]['Description'].includes(filterValue.substring(1, filterValue.length)) || items[i]['Title'].includes(filterValue.substring(1, filterValue.length)))) {
                result.push(items[i])
            }
        } else if (filterValue.substring(0, 12) === "Description:" && items[i]['Description'].includes(filterValue.substring(12, filterValue.length))) {
            result.push(items[i])
        } else if (items[i]['Title'].includes(filterValue) || items[i]['Description'].includes(filterValue)) {
            result.push(items[i])
        }
    }

    return result
}

function redMode() {
    console.log("toggle theme")
    let element = document.body;
    let red_button = document.getElementById("red-theme-button");
    let blue_button = document.getElementById("blue-theme-button");
    element.className = "red-mode";
    red_button.innerText = "Red Mode is ON";
    blue_button.innerText = "Blue Mode is OFF";
}

function blueMode() {
    let element = document.body;
    let blue_button = document.getElementById("blue-theme-button");
    let red_button = document.getElementById("red-theme-button");
    element.className = "blue-mode";
    blue_button.innerText = "Blue Mode in ON";
    red_button.innerText = "Red Mode in OFF";
}

// function increaseFont() {
//     console.log("increaseFont")
//     let element = document.getElementById("doNotModifyThisId_QuestionsTableBody");
//     element.className = "increase-font";
// }
function increaseFont() {
    txt = document.getElementById('doNotModifyThisId_QuestionsTableBody');
    style = window.getComputedStyle(txt, null).getPropertyValue('font-size');
    currentSize = parseFloat(style);
    console.log(currentSize);
    if (currentSize <= 25){
        txt.style.fontSize = (currentSize + 1) + 'px';
    }
}

function decreaseFont() {
    txt = document.getElementById('doNotModifyThisId_QuestionsTableBody');
    style = window.getComputedStyle(txt, null).getPropertyValue('font-size');
    currentSize = parseFloat(style);
    console.log(currentSize);
    if (currentSize >= 3){
        txt.style.fontSize = (currentSize - 1) + 'px';
    }
}