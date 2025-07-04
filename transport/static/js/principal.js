/*
const adulte = document.querySelector(".passager");
const dropDown = document.querySelector(".drop-down");
const dropDowncontent = document.querySelector(".dropdown-content");

// les classes des boutons plus et moins pour ajouter et retirer 
const btn_adl_more = document.querySelector(".btn-more-adl");
const btn_adl_manus = document.querySelector(".btn-manus-adl");
let countAdulte = 1;

const btn_enf_more = document.querySelector(".btn-more-enf");
const btn_enf_manus = document.querySelector(".btn-manus-enf");
let countEnfant = 0;

const btn_bg_more = document.querySelector(".btn-more-bg");
const btn_bg_manus = document.querySelector(".btn-manus-bg");
let countBagage = 0;

// les nombres renseignes par le client 

const nb_enf = document.getElementById("nbr-enf");
const nb_adl = document.getElementById("nbr-adl");
const nb_bga = document.getElementById("nbr-bga");

// le bouton qui remplit la barre passager 
const passager_fill = document.getElementById("btn-passager");
const mystyle = document.querySelector(".mystyle");

// nous recuperons les valeurs d'aller et de retour 
document.addEventListener("DOMContentLoaded", function () {
  // Gestion affichage date retour
  const k = document.getElementById("aller");
  const retour = document.querySelector(".date-retour");

  if (k && retour) {
    k.addEventListener("change", function () {
      if (k.checked === true) {
        console.log("aller checked");
        retour.style.display = "block";
      } else {
        console.log("aller unchecked");
        retour.style.display = "none";
      }
    });
  }

  const Rcheck = document.getElementById("retour");
  if (Rcheck && retour) {
    Rcheck.addEventListener("click", () => {
      if (Rcheck.checked === true) {
        console.log("retour checked");
        retour.style.display = "block";
      } else {
        retour.style.display = "none";
      }
    });
  }

  // Gestion des compteurs
  function bindCounter(btnPlusSelector, btnMinusSelector, inputId, initial = 0, min = 0) {
    const btnPlus = document.querySelector(btnPlusSelector);
    const btnMinus = document.querySelector(btnMinusSelector);
    const input = document.getElementById(inputId);
    let count = initial;

    if (btnPlus && input) {
      btnPlus.addEventListener("click", () => {
        count += 1;
        input.value = count;
      });
    }

    if (btnMinus && input) {
      btnMinus.addEventListener("click", () => {
        count = Math.max(min, count - 1);
        input.value = count;
      });
    }
  }

  bindCounter(".btn-more-adl", ".btn-manus-adl", "nbr-adl", 1);
  bindCounter(".btn-more-enf", ".btn-manus-enf", "nbr-enf", 0);
  bindCounter(".btn-more-bg", ".btn-manus-bg", "nbr-bga", 0);
});


// Fonction pour remplir le champ passager_fill

document.addEventListener("DOMContentLoaded", function () {
  const dropDown = document.getElementById("dropdown-btn");
  const dropDowncontent = document.getElementById("dropdown-content");
  const passager_fill = document.getElementById("passager-fill");

  const nb_adl = document.getElementById("nbr-adl");
  const nb_enf = document.getElementById("nbr-enf");
  const nb_bga = document.getElementById("nbr-bga");

  if (dropDown && dropDowncontent && passager_fill && nb_adl && nb_enf && nb_bga) {
    dropDown.addEventListener("click", () => {
      dropDowncontent.classList.toggle("mystyle");

      // Ici ton code pour remplir passager_fill exactement comme tu l’as fourni
      let text = `${nb_adl.value} ${nb_adl.value == 1 ? "Adulte" : "Adultes"}`;
      if (nb_enf.value > 0) {
        text += `, ${nb_enf.value} ${nb_enf.value == 1 ? "Enfant" : "Enfants"}`;
      }
      if (nb_bga.value > 0) {
        text += `, ${nb_bga.value} ${nb_bga.value == 1 ? "Bagage" : "Bagages"}`;
      }
      passager_fill.innerHTML = text;
    });
  }
});
*/

// Fonction pour fermer le dropdown si on clique en dehors
// cette partie remplace l'ancienne fonction qui fermait le dropdown
window.addEventListener("DOMContentLoaded", function () {
//document.addEventListener("DOMContentLoaded", function () {
  const toggleBtn = document.getElementById("btn-passager");
  const menu = document.getElementById("passenger-menu");

  let isVisible = false;

  toggleBtn.addEventListener("click", function (e) {
    e.stopPropagation(); // évite de propager le clic
    isVisible = !isVisible;
    menu.style.display = isVisible ? "block" : "none";
  });

  // Fermer le menu si on clique ailleurs
  document.addEventListener("click", function (e) {
    if (!menu.contains(e.target) && e.target !== toggleBtn) {
      menu.style.display = "none";
      isVisible = false;
    }
  });

  // 🔼 Gestion des boutons adultes
  document.querySelector(".btn-more-adl").addEventListener("click", () => {
    let val = parseInt(document.getElementById("nbr-adl").value) || 0;
    document.getElementById("nbr-adl").value = val + 1;
    updateLabel();
  });

  document.querySelector(".btn-manus-adl").addEventListener("click", () => {
    let val = parseInt(document.getElementById("nbr-adl").value) || 0;
    if (val > 1) {
      document.getElementById("nbr-adl").value = val - 1;
      updateLabel();
    }
  });

  // 🔼 Enfants
  document.querySelector(".btn-more-enf").addEventListener("click", () => {
    let val = parseInt(document.getElementById("nbr-enf").value) || 0;
    document.getElementById("nbr-enf").value = val + 1;
    updateLabel();
  });

  document.querySelector(".btn-manus-enf").addEventListener("click", () => {
    let val = parseInt(document.getElementById("nbr-enf").value) || 0;
    if (val > 0) {
      document.getElementById("nbr-enf").value = val - 1;
      updateLabel();
    }
  });

  // 🔼 Bagages
  document.querySelector(".btn-more-bg").addEventListener("click", () => {
    let val = parseInt(document.getElementById("nbr-bga").value) || 0;
    document.getElementById("nbr-bga").value = val + 1;
    updateLabel();
  });

  document.querySelector(".btn-manus-bg").addEventListener("click", () => {
    let val = parseInt(document.getElementById("nbr-bga").value) || 0;
    if (val > 0) {
      document.getElementById("nbr-bga").value = val - 1;
      updateLabel();
    }
  });

  // 🔁 Met à jour le résumé visible dans #btn-passager
  function updateLabel() {
    const adl = document.getElementById("nbr-adl").value;
    const enf = document.getElementById("nbr-enf").value;
    const bga = document.getElementById("nbr-bga").value;
    document.getElementById("btn-passager").textContent =
      `${adl} adulte${adl > 1 ? 's' : ''}` +
      (enf > 0 ? `, ${enf} enfant${enf > 1 ? 's' : ''}` : "") +
      (bga > 0 ? `, ${bga} bagage${bga > 1 ? 's' : ''}` : "");
  }
});

//});
// Ferme le dropdown si on clique en dehors





