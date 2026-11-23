# Alpha Vision — WhatsApp Cloud API Setup Guide
**Audience:** Non-technical administrators  
**Estimated Time:** 10–15 minutes  

---

## ACTION REQUIRED — Connect Your Official Meta WhatsApp Account

Follow these step-by-step instructions. Antigravity cannot sign into your Meta account on your behalf for security reasons.

---

### Step 1: Open Meta for Developers
1. Navigate to: **[https://developers.facebook.com/apps](https://developers.facebook.com/apps)**
2. Sign in with the Facebook account that has Admin permissions on your **Alpha Vision Method** Business Portfolio.

---

### Step 2: Create or Select Your WhatsApp App
1. If you already have an app for WhatsApp: Click on it.
2. If creating a new app:
   - Click the green **Create App** button.
   - For *Use Case*, select **Other** → Click **Next**.
   - Select **Business** as the app type → Click **Next**.
   - App Name: `Alpha Vision WhatsApp`.
   - Business Account: Select **Alpha Vision Method**.
   - Click **Create App**.

---

### Step 3: Add the WhatsApp Product
1. In your app dashboard, scroll down to the **Add products to your app** section.
2. Find **WhatsApp** and click **Set Up**.
3. In the left navigation menu, click **WhatsApp** → **API Setup**.
4. You will see:
   - **Phone Number ID** (e.g. `102938475610293`)
   - **WhatsApp Business Account ID (WABA ID)** (e.g. `987654321098765`)
5. Copy both values.

---

### Step 4: Generate a Permanent System User Token
> [!IMPORTANT]
> Do NOT use the 24-hour Temporary Access Token from the API Setup page in production. Create a permanent System User Token:
1. Open **[Meta Business Settings](https://business.facebook.com/settings)**.
2. In the left menu, go to **Users** → **System Users**.
3. Click **Add** → Name: `AlphaVision WhatsApp Engine` → Role: **Admin**.
4. Click **Assign Assets** → Select **Apps** → Choose `Alpha Vision WhatsApp` → Enable **Full Control**.
5. Click **Generate New Token**:
   - Select App: `Alpha Vision WhatsApp`.
   - Token Expiration: **Never**.
   - Select Scopes:
     - `whatsapp_business_messaging`
     - `whatsapp_business_management`
6. Click **Generate Token** and copy the resulting string (starts with `EAA...`).

---

### Step 5: Configure the Webhook
1. Back in Meta for Developers, navigate to **WhatsApp** → **Configuration**.
2. Under **Webhook**, click **Edit**:
   - **Callback URL:** `https://your-public-domain.com/api/whatsapp/webhook`
   - **Verify Token:** `alpha_vision_meta_wa_2026_webhook_verify`
3. Click **Verify and Save**.
4. Under **Webhook fields**, click **Manage** and subscribe to:
   - `messages`

---

### Step 6: Save Values in Alpha Vision OS
Enter these values into your `.env` file or directly into the **WhatsApp Integration Center** at `http://localhost:8000/whatsapp`:
```env
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_WABA_ID=your_waba_id
META_PHONE_NUMBER_ID=your_phone_number_id
META_ACCESS_TOKEN=your_permanent_system_user_token
META_WEBHOOK_VERIFY_TOKEN=alpha_vision_meta_wa_2026_webhook_verify
```

---

### Step 7: Send Your First Test Message
1. Open `http://localhost:8000/whatsapp`.
2. Enter your authorized personal WhatsApp number in **Send Safe Test Message**.
3. Click **Send Test Message Now**.
4. Verify instant delivery on your mobile phone!
