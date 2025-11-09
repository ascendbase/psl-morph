# Resend Email Verification Setup Guide

This guide will help you set up Resend for email verification in your PSL Morph application. Resend is the perfect choice for your requirements: free, reliable, no domain verification needed, and works seamlessly with Railway.

## Why Resend?

✅ **Free & Generous**: 3,000 emails/month free (vs 100 with many alternatives)  
✅ **No Domain Verification**: Can send from any email address  
✅ **Railway Compatible**: HTTPS API, no SMTP port issues  
✅ **Developer-Friendly**: Simple REST API, excellent documentation  
✅ **Reliable**: Built by the team behind React Email  
✅ **No Credit Card**: Free tier doesn't require payment info  

## Step 1: Create Resend Account

1. Go to [https://resend.com](https://resend.com)
2. Click "Sign Up" 
3. Create account with your email
4. Verify your email address
5. Complete the onboarding process

## Step 2: Get Your API Key

1. After logging in, go to the **API Keys** section
2. Click "Create API Key"
3. Give it a name like "PSL Morph Production"
4. Select "Sending access" permissions
5. Click "Add"
6. **Copy the API key immediately** (you won't see it again)

## Step 3: Update Environment Variables

Update your `.env` file with the Resend configuration:

```env
# Resend Email Configuration
RESEND_API_KEY=re_your_api_key_here
RESEND_FROM_EMAIL=your-email@gmail.com
RESEND_FROM_NAME=PSL Morph
BASE_URL=http://localhost:5000
```

### Environment Variables Explained:

- **RESEND_API_KEY**: Your Resend API key (starts with `re_`)
- **RESEND_FROM_EMAIL**: The email address emails will appear to come from (can be your Gmail)
- **RESEND_FROM_NAME**: The display name for your emails
- **BASE_URL**: Your app's URL (update for production: `https://your-app.railway.app`)

## Step 4: Test Locally

1. Run the test script to verify everything works:
   ```bash
   python test_resend_email.py
   ```

2. Or use the Windows batch file:
   ```bash
   test_resend_email.bat
   ```

## Step 5: Deploy to Railway

1. **Add Environment Variables to Railway:**
   - Go to your Railway project dashboard
   - Click on your service
   - Go to "Variables" tab
   - Add each environment variable:
     - `RESEND_API_KEY` = your API key
     - `RESEND_FROM_EMAIL` = your email
     - `RESEND_FROM_NAME` = PSL Morph
     - `BASE_URL` = https://your-app.railway.app

2. **Deploy your updated code:**
   ```bash
   git add .
   git commit -m "Switch to Resend for email verification"
   git push origin main
   ```

3. **Railway will automatically redeploy** with the new email system

## Step 6: Verify Production

1. Visit your Railway app
2. Try registering a new account
3. Check your email for the verification message
4. Click the verification link to confirm it works

## Email Features

### Verification Email
- Professional HTML design with PSL Morph branding
- Clear call-to-action button
- Fallback link for email clients that don't support buttons
- 24-hour expiration notice
- Mobile-responsive design

### Welcome Email
- Sent after successful email verification
- Lists all available features
- Direct link to dashboard
- Professional branding

## Troubleshooting

### Common Issues:

**1. "RESEND_API_KEY not found"**
- Make sure you've added the API key to your environment variables
- Check that the variable name is exactly `RESEND_API_KEY`
- Restart your application after adding environment variables

**2. "Failed to send email: 401"**
- Your API key is invalid or expired
- Generate a new API key from Resend dashboard
- Make sure you copied the full key (starts with `re_`)

**3. "Failed to send email: 422"**
- Check that your from_email is valid
- Ensure the email format is correct
- Verify the recipient email is valid

**4. Emails not arriving**
- Check spam/junk folders
- Verify the recipient email address is correct
- Check Resend dashboard for delivery status

### Testing Commands:

```bash
# Test API key validity
python -c "
import os, requests
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('RESEND_API_KEY')
headers = {'Authorization': f'Bearer {api_key}'}
response = requests.get('https://api.resend.com/domains', headers=headers)
print(f'Status: {response.status_code}')
print(f'Response: {response.text}')
"

# Test email sending
python test_resend_email.py
```

## Free Tier Limits

- **3,000 emails per month** (more than enough for most applications)
- **No daily limits**
- **No credit card required**
- **All features included**

## Production Considerations

1. **Monitor Usage**: Check your Resend dashboard regularly
2. **Set Up Webhooks**: Get delivery confirmations (optional)
3. **Custom Domain**: Add your own domain for better deliverability (optional)
4. **Rate Limiting**: Resend handles this automatically

## Security Best Practices

1. **Keep API Key Secret**: Never commit it to version control
2. **Use Environment Variables**: Always store in `.env` files
3. **Rotate Keys**: Generate new keys periodically
4. **Monitor Usage**: Watch for unusual activity

## Next Steps

Once email verification is working:

1. **Test the complete flow**: Registration → Email → Verification → Login
2. **Monitor email delivery**: Check Resend dashboard for analytics
3. **Consider additional features**: Welcome sequences, password reset emails
4. **Scale as needed**: Upgrade to paid plan when you exceed 3,000 emails/month

## Support

- **Resend Documentation**: [https://resend.com/docs](https://resend.com/docs)
- **Resend Support**: Available through their dashboard
- **API Reference**: [https://resend.com/docs/api-reference](https://resend.com/docs/api-reference)

---

Your email verification system is now ready to prevent account abuse and ensure only verified users can access PSL Morph! 🎉
