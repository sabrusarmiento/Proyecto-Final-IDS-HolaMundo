document.addEventListener('DOMContentLoaded', () => {
    const toggleSwitch = document.querySelector('#checkbox');
    if (!toggleSwitch) return;

    toggleSwitch.checked = localStorage.getItem('theme') === 'dark';

    toggleSwitch.addEventListener('change', (e) => {
        const theme = e.target.checked ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        window.dispatchEvent(new Event('themeChanged'));
    });
});
