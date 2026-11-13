importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging-compat.js');

// Default config for development/mock. Will be updated with real credentials.
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_AUTH_DOMAIN",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_STORAGE_BUCKET",
    messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    appId: "YOUR_APP_ID"
};

firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage(function(payload) {
    console.log('[firebase-messaging-sw.js] Received background message ', payload);

    const notificationTitle = payload.notification.title;
    const notificationOptions = {
        body: payload.notification.body,
        icon: '/static/icons/pill.png',
        data: payload.data,
        actions: [
            {action: 'taken', title: '✅ Mark as Taken'},
            {action: 'snooze', title: '⏰ Snooze (15m)'},
            {action: 'skipped', title: '❌ Skip'}
        ]
    };

    self.registration.showNotification(notificationTitle, notificationOptions);
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    
    const action = event.action;
    const data = event.notification.data;
    
    if (action === 'taken' || action === 'snooze' || action === 'skipped') {
        event.waitUntil(
            fetch('/api/notification_action/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    log_id: data.log_id,
                    action: action
                })
            })
        );
    } else {
        // Open the app if just clicking the notification body
        clients.openWindow('/');
    }
});
