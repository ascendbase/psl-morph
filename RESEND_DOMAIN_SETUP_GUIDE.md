# Resend Domain Setup Guide for ascendbase.pro

## Overview
This guide provides step-by-step instructions for setting up your custom domain `ascendbase.pro` with Resend for professional email delivery.

## 🎯 Benefits of Custom Domain
- **Professional Branding**: Emails from `noreply@ascendbase.pro` instead of generic addresses
- **Better Deliverability**: Custom domains have higher trust scores
- **Brand Recognition**: Users see your domain in verification emails
- **No Restrictions**: Full control over email sending

## 🚀 Step-by-Step Setup

### Step 1: Access Resend Dashboard
1. Go to [resend.com](https://resend.com)
2. Sign up for a free account
3. Navigate to the **Domains** section in the sidebar

### Step 2: Add Your Domain
1. Click **"Add Domain"** button
2. Enter your domain: `ascendbase.pro`
3. Click **"Add Domain"**

### Step 3: DNS Verification
Resend will provide you with DNS records to add to your domain. You'll need to add these records to your domain registrar or DNS provider.

#### Required DNS Records:
```
Type: TXT
Name: @
Value: resend-verification=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

Type: MX
Name: @
Value: feedback-smtp.resend.com
Priority: 10

Type: TXT
Name: @
Value: v=spf1 include:_spf.resend.com ~all

Type: TXT
Name: resend._domainkey
Value: p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC... (long key)

Type: CNAME
Name: rs._domainkey
Value: rs.resend.com
```

### Step 4: Add DNS Records to Your Domain
1. Log into your domain registrar (where you bought `ascendbase.pro`)
2. Navigate to DNS management section
3. Add each DNS record provided by Resend
4. Save the changes

**Common Domain Registrars:**
- **Namecheap**: Advanced DNS → Add Record
- **GoDaddy**: DNS Management → Add Record
- **Cloudflare**: DNS → Add Record
- **Google Domains**: DNS → Custom Records

### Step 5: Verify Domain
1. Return to Resend dashboard
2. Click **"Verify Domain"** next to `ascendbase.pro`
3. Wait for verification (can take up to 24 hours)
4. You'll see a green checkmark when verified

### Step 6: Create API Key
1. Navigate to **API Keys** section
2. Click **"Create API Key"**
3. Give it a name: `PSL Morph Production`
4. Copy the API key (starts with `re_`)
5. Store it securely

## 🔧 Configuration

### Update Environment Variables
Once your domain is verified, update your environment variables:

#### Local (.env file):
```bash
RESEND_API_KEY=re_your_actual_api_key_here
RESEND_FROM_EMAIL=noreply@ascendbase.pro
RESEND_FROM_NAME=PSL Morph
```

#### Railway Production:
```bash
RESEND_API_KEY=re_your_actual_api_key_here
RESEND_FROM_EMAIL=noreply@ascendbase.pro
RESEND_FROM_NAME=PSL Morph
```

## ✅ Verification Checklist

- [ ] Domain added to Resend
- [ ] DNS records added to domain registrar
- [ ] Domain verified (green checkmark)
- [ ] API key created and copied
- [ ] Environment variables updated
- [ ] Test email sent successfully

## 🧪 Testing Your Setup

### Test Email Sending
```bash
# Run the test script
python test_resend_email.py

# Or test directly
python -c "
from email_utils import send_verification_email
result = send_verification_email('your-email@gmail.com', 'test_token_123')
print('Success!' if result else 'Failed!')
"
```

### Expected Results
- ✅ Email sent from `noreply@ascendbase.pro`
- ✅ Professional PSL Morph branding
- ✅ No spam folder delivery
- ✅ High deliverability rates

## 🛠️ Troubleshooting

### Common Issues

#### 1. Domain Not Verifying
- **Wait Time**: DNS propagation can take up to 24 hours
- **Check Records**: Ensure all DNS records are added correctly
- **TTL Settings**: Set TTL to 300 seconds for faster propagation

#### 2. DNS Record Errors
- **Exact Values**: Copy DNS values exactly as provided by Resend
- **No Extra Spaces**: Remove any leading/trailing spaces
- **Correct Type**: Ensure record type (TXT, MX, CNAME) is correct

#### 3. Email Not Sending
- **Domain Status**: Verify domain shows as "Verified" in Resend
- **API Key**: Ensure you're using the correct API key
- **From Email**: Must use `@ascendbase.pro` domain

### Debug Commands
```bash
# Check DNS propagation
nslookup -type=TXT ascendbase.pro

# Test API connection
python -c "
import requests
headers = {'Authorization': 'Bearer YOUR_API_KEY'}
response = requests.get('https://api.resend.com/domains', headers=headers)
print(f'Status: {response.status_code}')
print(response.json())
"
```

## 📊 Domain Benefits

### Free Tier with Custom Domain
- **3,000 emails/month** (same as without domain)
- **100 emails/day** (same as without domain)
- **Professional appearance**
- **Better deliverability**
- **Brand recognition**

### Email Analytics
- Open rates tracking
- Click tracking
- Bounce handling
- Delivery confirmations

## 🔗 Useful Resources

- [Resend Domain Setup](https://resend.com/docs/dashboard/domains/introduction)
- [DNS Record Types](https://resend.com/docs/dashboard/domains/dns-records)
- [Domain Verification](https://resend.com/docs/dashboard/domains/verify)
- [Troubleshooting Guide](https://resend.com/docs/dashboard/domains/troubleshooting)

## 📞 Support

If you encounter issues:
1. Check Resend documentation
2. Verify DNS records with your registrar
3. Wait 24 hours for DNS propagation
4. Contact Resend support if needed

Your custom domain setup will provide professional email delivery for the PSL Morph verification system!
