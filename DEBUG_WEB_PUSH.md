# Web Push Debugging Guide

## Step-by-Step Troubleshooting

### 1. Check VAPID Configuration

**API Endpoint:**
```bash
GET /vapid/debug
Authorization: Bearer YOUR_TOKEN
```

**Expected Response:**
```json
{
  "vapid_configured": true,
  "vapid_public_key_set": true,
  "vapid_private_key_set": true,
  "vapid_subject": "mailto:your-email@example.com",
  "user_id": 1,
  "subscription_count": 1,
  "subscriptions": [...]
}
```

**If `vapid_configured` is false:**
- Check your `.env` file has `VAPID_PUBLIC_KEY` and `VAPID_PRIVATE_KEY`
- Restart your server after adding them

### 2. Check Database Migration

Verify the `push_subscriptions` table exists:

```bash
alembic upgrade head
```

### 3. Verify Subscription is Saved

After subscribing from the frontend:

**API Endpoint:**
```bash
GET /vapid/debug
Authorization: Bearer YOUR_TOKEN
```

Check that `subscription_count` > 0

### 4. Test Push Manually

**Close your browser tab completely**, then:

**API Endpoint:**
```bash
POST /push-subscriptions/test
Authorization: Bearer YOUR_TOKEN
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Test push notification sent to 1 subscription(s)",
  "user_id": 1
}
```

You should see a system notification!

### 5. Check Server Logs

When a notification is created, you should see logs like:

```
[NOTIFICATION SYNC] User 2 connected: False
[NOTIFICATION SYNC] User 2 is offline, triggering web push
[WEB PUSH] Scheduling web push for user 2
[WEB PUSH] Attempting to send web push to user 2
[WEB PUSH] Found 1 subscription(s) for user 2
[WEB PUSH] Sending to endpoint: https://fcm.googleapis.com/fcm/send/...
[WEB PUSH] Successfully sent push notification to user 2
```

### 6. Common Issues

#### Issue: "No subscriptions found"

**Solution:** Frontend needs to call `/push-subscriptions/` POST endpoint after getting permission

**Frontend Code:**
```javascript
const subscription = await registration.pushManager.subscribe({
  userVisibleOnly: true,
  applicationServerKey: urlBase64ToUint8Array(publicKey)
});

await fetch('http://localhost:8000/push-subscriptions/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(subscription.toJSON())
});
```

#### Issue: "VAPID keys missing"

**Solution:**
1. Generate keys: `vapid --gen`
2. Add to `.env`:
   ```
   VAPID_PUBLIC_KEY=your_public_key
   VAPID_PRIVATE_KEY=your_private_key
   VAPID_SUBJECT=mailto:your-email@example.com
   ```
3. Restart server

#### Issue: Notifications only work when site is open

**Solution:** The user is detected as "online" (Socket.IO connected)
- Web push only sends when user is offline
- **Close the browser tab completely** to test
- Check logs for: `User X is offline, triggering web push`

#### Issue: 404/410 errors in logs

**Solution:** Browser subscription expired
- Re-subscribe from the frontend
- Stale subscriptions are automatically cleaned up

### 7. Frontend Service Worker Check

Verify your service worker has the push event listener:

```javascript
// service-worker.js
self.addEventListener('push', function(event) {
  console.log('Push received:', event);
  
  const data = event.data.json();
  
  const options = {
    body: data.body,
    icon: '/icon.png',
    badge: '/badge.png',
    data: data.data
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});
```

### 8. Browser Console Check

Open DevTools Console and check for:

```javascript
// Check if service worker is registered
navigator.serviceWorker.ready.then(reg => {
  console.log('Service Worker ready:', reg);
});

// Check if push is subscribed
navigator.serviceWorker.ready.then(reg => {
  reg.pushManager.getSubscription().then(sub => {
    console.log('Push subscription:', sub);
  });
});
```

### 9. Test Flow

1. **Open your app** in browser
2. **Subscribe to push** (grant permission)
3. **Verify subscription saved:** `GET /vapid/debug` shows subscription_count > 0
4. **Close browser tab completely**
5. **From another account/device:** like, comment, or follow the first user
6. **Check if notification appears** on the device (even with browser closed)

### 10. Manual Test Without Closing Browser

Use the test endpoint:

```bash
curl -X POST http://localhost:8000/push-subscriptions/test \
  -H "Authorization: Bearer YOUR_TOKEN"
```

This forces a push notification regardless of online status.

## Quick Checklist

- [ ] VAPID keys in `.env`
- [ ] Server restarted after adding VAPID keys
- [ ] Database migration run (`alembic upgrade head`)
- [ ] Service worker registered in browser
- [ ] Push permission granted
- [ ] Subscription saved (check `/vapid/debug`)
- [ ] Browser tab closed completely when testing
- [ ] Check server logs for `[WEB PUSH]` messages

## Still Not Working?

Share the output of:
1. `GET /vapid/debug` response
2. Server logs when triggering a notification
3. Browser console errors
4. Result of `POST /push-subscriptions/test`
