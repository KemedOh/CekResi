// Fungsi untuk tombol salin
document.querySelector('.copy-btn')?.addEventListener('click', function () {
    const resiNumber = document.querySelector('.resi-number span').textContent.replace('No. Resi: ', '');
    navigator.clipboard.writeText(resiNumber);

    const originalText = this.innerHTML;
    this.innerHTML = '<i class="fas fa-check"></i> Tersalin';

    setTimeout(() => {
        this.innerHTML = originalText;
    }, 2000);
});

// Fungsi untuk tombol refresh
document.querySelector('.refresh-btn')?.addEventListener('click', function () {
    const icon = this.querySelector('i');
    icon.style.transform = 'rotate(360deg)';

    setTimeout(() => {
        icon.style.transform = 'rotate(0)';
        location.reload(); // Refresh halaman
    }, 1000);
});

// Animasi progress bar
function animateProgress() {
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        let width = 0;
        const targetWidth = progressBar.parentElement.dataset.progress || '65';
        const interval = setInterval(() => {
            if (width >= parseInt(targetWidth)) {
                clearInterval(interval);
            } else {
                width++;
                progressBar.style.width = width + '%';
            }
        }, 20);
    }
}

window.addEventListener('load', animateProgress);