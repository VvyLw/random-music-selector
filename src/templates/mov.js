window.addEventListener('load', () => {
    const iframe = document.querySelector('.video-container iframe');
    const container = document.querySelector('.video-container');
    iframe.addEventListener('load', () => {
        const videoWidth = iframe.contentWindow.document.body.scrollWidth;
        const videoHeight = iframe.contentWindow.document.body.scrollHeight;
        const aspectRatio = videoHeight / videoWidth;
        container.style.paddingTop = (aspectRatio * 100) + '%';
    });
});