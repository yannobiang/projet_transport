const adulte = document.querySelector(".passager");
const dropDown = document.querySelector(".drop-down");
const dropDowncontent = document.querySelector(".dropdown-content");
const btn_adl_more = document.querySelector(".btn-more-adl");
const btn_adl_manus = document.querySelector(".btn-manus-adl");
const btn_enf_more = document.querySelector(".btn-more-enf");
const btn_enf_manus = document.querySelector(".btn-manus-enf");
const btn_bg_more = document.querySelector(".btn-more-bg");
const btn_bg_manus = document.querySelector(".btn-manus-bg");
const nb_enf = document.getElementById("nbr-enf");
const nb_adl = document.getElementById("nbr-adl");
const nb_bga = document.getElementById("nbr-bga");

dropDown.addEventListener("click", () => {
  console.log(dropDowncontent);
  dropDowncontent.classList.toggle("mystyle");
});
