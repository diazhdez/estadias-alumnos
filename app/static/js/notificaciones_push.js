const VAPID_PUBLIC_KEY = "BKT8mVwq7_lF2LJX0x5pK1G6xZJl3Y5D9Tt0GZocJXwQ7DdQG6GgE6kP0q1q3iP3xGzS7e5V9l7ZcRtxkZJ3t5g";

function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');
    const rawData = window.atob(base64);
    return Uint8Array.from([...rawData].map(char => char.charCodeAt(0)));
}

if ('serviceWorker' in navigator && 'PushManager' in window) {
    navigator.serviceWorker.register('/static/sw.js')
    .then(registration => {
        console.log('SW registrado:', registration.scope);
        return Notification.requestPermission()
        .then(permission => {
            if(permission !== "granted") throw new Error("Permiso denegado");
            return registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
            });
        })
        .then(subscription => {
            console.log("Suscripción push:", subscription);
            fetch('/subscribe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(subscription)
            });
        });
    })
    .catch(err => console.error("Error SW/Push:", err));
}
