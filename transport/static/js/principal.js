const adulte = document.querySelector(".passager");
const dropDown = document.querySelector(".drop-down");
const dropDowncontent = document.querySelector(".dropdown-content");

/* les classes des boutons plus et moins pour ajouter et retirer */
const btn_adl_more = document.querySelector(".btn-more-adl");
const btn_adl_manus = document.querySelector(".btn-manus-adl");
let countAdulte = 1;

const btn_enf_more = document.querySelector(".btn-more-enf");
const btn_enf_manus = document.querySelector(".btn-manus-enf");
let countEnfant = 0;

const btn_bg_more = document.querySelector(".btn-more-bg");
const btn_bg_manus = document.querySelector(".btn-manus-bg");
let countBagage = 0;

/* les nombres renseignes par le client */

const nb_enf = document.getElementById("nbr-enf");
const nb_adl = document.getElementById("nbr-adl");
const nb_bga = document.getElementById("nbr-bga");

/* le bouton qui remplit la barre passager */
const passager_fill = document.getElementById("btn-passager");
const mystyle = document.querySelector(".mystyle");

/* nous recuperons les valeurs d'aller et de retour */

let Rcheck = document.getElementById("retour");
let Acheck = document.getElementById("aller");
const dateretour = document.querySelector(".date-retour");
/*const dateretour2 = document.querySelector(".date-retour2");*/

/* les fonctions utilisees par le proramme */

function myFunction(event) {
  if (Rcheck.checked == true && Acheck.checked == false) {
    document.querySelector(".date-retour").style.display = "block";
  } else {
    document.querySelector(".date-retour").style.display = "none";
  }
}
/* modification du compte nombre des adultes */

btn_adl_more.addEventListener("click", () => {
  countAdulte += 1;
  nb_adl.value = countAdulte;
});
btn_adl_manus.addEventListener("click", () => {
  countAdulte -= 1;

  if (countAdulte > 0) {
    nb_adl.value = countAdulte;
  } else {
    nb_adl.value = 0;
  }
});

/* modification du compte nombre des enfants */

btn_enf_more.addEventListener("click", () => {
  countEnfant += 1;
  nb_enf.value = countEnfant;
});
btn_enf_manus.addEventListener("click", () => {
  countEnfant -= 1;
  if (countEnfant > 0) {
    nb_enf.value = countEnfant;
  } else {
    nb_enf.value = 0;
  }
});

/* modification du compte nombre des bagages */

btn_bg_more.addEventListener("click", () => {
  countBagage += 1;
  nb_bga.value = countBagage;
});

btn_bg_manus.addEventListener("click", () => {
  countBagage -= 1;
  if (countBagage > 0) {
    nb_bga.value = countBagage;
  } else {
    nb_bga.value = 0;
  }
});

dropDown.addEventListener("click", () => {
  dropDowncontent.classList.toggle("mystyle");

  if (nb_adl.value > 1) {
    passager_fill.innerHTML = nb_adl.value + " " + "Adultes";
    if (nb_enf.value > 1) {
      passager_fill.innerHTML += ", " + nb_enf.value + " " + "Enfants";
      if (nb_bga.value > 1) {
        passager_fill.innerHTML += ", " + nb_bga.value + " " + "Bagages";
      } else if (nb_bga.value == 1) {
        passager_fill.innerHTML += ", " + nb_bga.value + " " + "Bagage";
      }
    } else if (nb_enf.value == 1) {
      passager_fill.innerHTML += ", " + nb_enf.value + " " + "Enfant";
      if (nb_bga.value > 1) {
        passager_fill.innerHTML += ", " + nb_bga.value + " " + "Bagages";
      } else if (nb_bga.value == 1) {
        passager_fill.innerHTML += ", " + nb_bga.value + " " + "Bagage";
      }
    } else {
      if (nb_bga.value > 1) {
        passager_fill.innerHTML += ", " + nb_bga.value + " " + "Bagages";
      } else if (nb_bga.value == 1) {
        passager_fill.innerHTML += ", " + nb_bga.value + " " + "Bagage";
      }
    }
  } else if (nb_adl.value == 1) {
    passager_fill.innerHTML = nb_adl.value + " " + "Adulte";

    if (nb_enf.value > 1) {
      passager_fill.innerHTML += ", " + nb_enf.value + " " + "Enfants";
      if (nb_bga.value > 1) {
        passager_fill.innerHTML += ", " + nb_bga.value + " " + "Bagages";
      } else if (nb_bga.value == 1) {
        passager_fill.innerHTML += ", " + nb_bga.value + " " + "Bagage";
      }
    } else if (nb_enf.value == 1) {
      passager_fill.innerHTML += ", " + nb_enf.value + " " + "Enfant";
      if (nb_bga.value > 1) {
        passager_fill.innerHTML += ", " + nb_bga.value + " " + "Bagages";
      } else if (nb_bga.value == 1) {
        passager_fill.innerHTML += ", " + nb_bga.value + " " + "Bagage";
      }
    } else {
      if (nb_bga.value > 1) {
        passager_fill.innerHTML += ", " + nb_bga.value + " " + "Bagages";
      } else if (nb_bga.value == 1) {
        passager_fill.innerHTML += ", " + nb_bga.value + " " + "Bagage";
      }
    }
  }
});

/* ajout de la possibilite de la date de retour */

Rcheck.addEventListener("change", myFunction);
