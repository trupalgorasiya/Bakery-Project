// ROTATING ARROWS AND SHOW AND HIDE DIV'S

const arrow = document.querySelectorAll(".fas");
const answer = document.querySelectorAll(".hide");
// console.log(arrow);
arrow.forEach((cur,i,arr)=>{cur.addEventListener("click",function()
    {
        cur.classList.toggle("rot");
        answer[i].classList.toggle("hide");
    }
)});