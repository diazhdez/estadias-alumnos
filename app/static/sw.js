// sw.js
const CACHE_NAME = "estadias-cache-v1";
const urlsToCache = [
    "/",
    "/static/css/style.css",
    "/static/js/main.js",
    "/app/static/img/LOGO-UTA 512x512.jpg",
    "/app/static/img/LOGO-UTA 192x192.jpg",
    "/EduLink/Vinculación/administrar_Alumnos",
    "/EduLink/Biblioteca/administrar_Alumnos",
    "/EduLink/Recursos/administrar_Alumnos",
    "/EduLink/Juridico/administrar_Alumnos",
    "/EduLink/Estadias/administrar_Alumnos",
    "/static/js/servicework.js",
    "/static/js/notificaciones_push.js",
    "/Edulink/Alumno",
    "/Edulink/Alumno/Archivos_Universidad",
    "/subscribe"

  
];
// sw.js
self.addEventListener("install", event => {
    console.log("Service Worker instalado");
    self.skipWaiting();
});

self.addEventListener("activate", event => {
    console.log("Service Worker activado");
});

self.addEventListener('push', function(event) {
    const data = event.data.json();
    event.waitUntil(
        self.registration.showNotification("Notificación", {
            body: data.body,
            data: { url: data.url }
        })
    );
});

self.addEventListener("notificationclick", event => {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data)
    );
});
