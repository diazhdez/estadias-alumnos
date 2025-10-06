// servicework.js
// Registra el Service Worker   
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function () {
                navigator.serviceWorker.register('/static/sw.js').then(function (registration) {
                    console.log('Service Worker registrado con éxito:',
                        registration.scope);
                }, function (err) {
                    console.log('Error al registrar el Service Worker:', err);
                });
            });
        }
