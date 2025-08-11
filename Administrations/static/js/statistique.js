document.addEventListener('DOMContentLoaded', function() {
  const ctxPie = document.getElementById('pieChart').getContext('2d');
  const ctxBar = document.getElementById('barChart').getContext('2d');

  const categories = window.chartData.categories;
  const totaux = window.chartData.totaux;

  // Couleurs personnalisées pour les secteurs du camembert
  const backgroundColors = ['#3498db', '#e74c3c', '#2ecc71', '#9b59b6', '#f39c12', '#1abc9c', '#34495e'];

  new Chart(ctxPie, {
    type: 'pie',
    data: {
      labels: categories,
      datasets: [{
        label: "Produits par catégorie",
        data: totaux,
        backgroundColor: backgroundColors.slice(0, categories.length),
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  });

  new Chart(ctxBar, {
    type: 'bar',
    data: {
      labels: categories,
      datasets: [{
        label: "Produits par catégorie",
        data: totaux,
        backgroundColor: '#3498db'
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          }
        }
      },
      plugins: {
        legend: {
          display: false
        }
      }
    }
  });
});
