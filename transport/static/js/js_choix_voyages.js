document.addEventListener("DOMContentLoaded", function () {
    const cardsPerPage = 3;
    const cards = document.querySelectorAll('#results-container .search-box');
    const totalPages = Math.ceil(cards.length / cardsPerPage);
    let currentPage = 1;
  
    function showPage(page) {
      cards.forEach((card, index) => {
        card.style.display = (index >= (page - 1) * cardsPerPage && index < page * cardsPerPage) ? 'block' : 'none';
      });
  
      document.getElementById('prev-btn').disabled = (page === 1);
      document.getElementById('next-btn').disabled = (page === totalPages);
    }
  
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
  
    if (prevBtn && nextBtn) {
      prevBtn.addEventListener('click', () => {
        if (currentPage > 1) {
          currentPage--;
          showPage(currentPage);
        }
      });
  
      nextBtn.addEventListener('click', () => {
        if (currentPage < totalPages) {
          currentPage++;
          showPage(currentPage);
        }
      });
  
      showPage(currentPage); // Initialisation
    }
  });

  document.addEventListener("DOMContentLoaded", function () {
    const retourCardsPerPage = 3;
    const retourCards = document.querySelectorAll('#results-retour-container .annonce');
    const retourTotalPages = Math.ceil(retourCards.length / retourCardsPerPage);
    let retourCurrentPage = 1;
  
    function showRetourPage(page) {
      retourCards.forEach((card, index) => {
        card.style.display = (index >= (page - 1) * retourCardsPerPage && index < page * retourCardsPerPage)
          ? 'block' : 'none';
      });
  
      document.getElementById('prev-retour-btn').disabled = (page === 1);
      document.getElementById('next-retour-btn').disabled = (page === retourTotalPages);
    }
  
    const prevRetourBtn = document.getElementById('prev-retour-btn');
    const nextRetourBtn = document.getElementById('next-retour-btn');
  
    if (prevRetourBtn && nextRetourBtn) {
      prevRetourBtn.addEventListener('click', () => {
        if (retourCurrentPage > 1) {
          retourCurrentPage--;
          showRetourPage(retourCurrentPage);
        }
      });
  
      nextRetourBtn.addEventListener('click', () => {
        if (retourCurrentPage < retourTotalPages) {
          retourCurrentPage++;
          showRetourPage(retourCurrentPage);
        }
      });
  
      showRetourPage(retourCurrentPage);
    }
  });