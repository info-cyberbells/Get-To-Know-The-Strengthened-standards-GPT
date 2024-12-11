// Check for file changes every 1 second
setInterval(() => {
    fetch(window.location.href, { method: 'HEAD' })
        .then(response => {
            const lastModified = response.headers.get('last-modified');
            if (!window.lastModified) {
                window.lastModified = lastModified;
            } else if (window.lastModified !== lastModified) {
                window.lastModified = lastModified;
                window.location.reload();
            }
        })
        .catch(error => console.error('Live reload check failed:', error));
}, 25000);
// Either remove this completely or modify it to exclude reloading during file uploads

