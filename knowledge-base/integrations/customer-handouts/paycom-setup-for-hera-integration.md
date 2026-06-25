# Paycom Setup for Your Hera Integration

**Audience:** Hera customers using Paycom
**Purpose:** Walks the customer through the Paycom-side prep work they must complete before connecting Paycom to Hera. Steps 1-3 here mirror steps 1-3 in [how-to-connect-paycom-to-hera.md](../how-to-connect-paycom-to-hera.md). The remaining connection steps (Magic Link entry, confirmation) happen in Hera after these are done.

---

## What this guide covers

This guide is for Hera customers who use Paycom for payroll and want to connect Paycom to Hera. There are three steps that must happen on the Paycom side before Hera can establish the connection. This document walks you through those three steps.

---

## Step 1: Request API access from Paycom

Reach out to your Paycom account representative and let them know you would like to enable API access. When they ask what the access is for, you can say:

> "I want a vendor to access my employee data from Paycom."

Your Paycom representative will then walk you through their standard approval process. Expect the following:

- Paycom may ask you to sign an NDA before sharing documentation.
- A discovery call will be scheduled with the Paycom Automation team and your technical resources to talk through what is available and the technical side of leveraging the API.
- You will review and sign a Paycom Proposal and MSA to add API access to your existing Paycom suite.

This step is handled entirely between you and Paycom. Plan for a few business days. You cannot move to Step 2 until Paycom approves API access.

---

## Step 2: Receive your Paycom API credentials

Once Paycom approves your API access, your Paycom representative will provide:

- **API SID** (System ID)
- **API Token**
- **Paycom API Documentation**

Keep these in a secure location. You will need both the SID and the Token in the final connection step in Hera.

---

## Step 3: Allowlist Hera's IP addresses in Paycom

Paycom only allows API access from specific, pre-approved IP addresses. Before the connection can succeed, your Paycom representative needs to add Hera's IP addresses to your allowlist.

Send your Paycom representative the following three IP addresses and ask them to add all of them:

- `13.59.40.132`
- `3.136.219.255`
- `18.216.194.37`

If any of these IPs are missing, the connection will fail when you try to complete it in Hera. Confirm directly with your Paycom representative that all three have been added before moving on.

---

## Reference

For Paycom's official process documentation, see the [Paycom Client API Checklist](https://files.hera.run/share/V4qy2ypZ9LTmFCXEofOw).

*For additional help, reach out to your Hera contact.*
