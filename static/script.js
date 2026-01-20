

const flash = document.querySelectorAll(".flash")

if (flash){
  setTimeout(() => {
    document.querySelectorAll(".flash").forEach(flash => {
      flash.style.opacity = "0";
      setTimeout(() => flash.remove(), 500);
    });
  }, 3000);

}




const circle = document.querySelector("#circle");
const box = document.querySelector("#box");
const close_box = document.querySelector("#close_box");
const password = document.querySelector("#password");
const showPassword = document.querySelector("#showPassword");
const delete_account = document.getElementById("delete_account")
const warning = document.getElementById("warning")
const delete_yes = document.getElementById("delete_no")
const delete_no = document.getElementById("delete_no")
const home = document.getElementById("home")



if (close_box) {
  close_box.addEventListener('click', () => {
    box.style.display = "none";
    chatBox.style.display = 'none';
  });
}

if (circle) {
  circle.addEventListener('click', () => {
    box.style.display = "flex";
    chatBox.style.display = 'none';
  });
}

if (showPassword && password) {
  showPassword.addEventListener('click', () => {
    if (password.type === "password") {
      password.type = "text";
      showPassword.innerText = 'Hide';
    } else {
      password.type = "password";
      showPassword.innerText = 'Show';
    }
  });
}

if (delete_account){

  delete_account.addEventListener('click', () =>{
    if (warning.style.display === "none" || warning.style.display === ""){
      warning.style.display = "block"
      box.style.display = "none";
      home.style.opacity="0.5"
      warning.style.opacity = "1"
    }
    else{
      warning.style.display = "none";
      
    }
  })

}

if (delete_yes || delete_no) {

  delete_yes.addEventListener('click', () => {
    
      warning.style.display = "none";
      home.style.opacity = "1"

  })

  delete_no.addEventListener('click', () => {
    warning.style.display = "none";

  })
}



 