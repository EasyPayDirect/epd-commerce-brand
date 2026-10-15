---
name: Revenue Recovery
slug: revenue-recovery
canonical_spelling: "Revenue Recovery"
aliases_incorrect:
  - "revenue recovery" # lowercase mid-sentence
  - "revenue-recovery"
  - "recovery"
  - "payment recovery"
  - "dunning"
capability: React
status: beta
proper_noun: true
one_liner: "Automatically retry failed payments and rescue at-risk revenue with rule-based strategies you preset or build yourself."
related_names:
  - "Recovery Templates"
  - "Order Rescue"
  - "Retry & Communication Logic"
  - "Billing Notifications"
  - "Email Templates"
  - "Optimized AI Strategy"
images:
  hero:
    src: assets/epd-commerce-features/revenue-recovery/1-landscape.png
    alt: The Order Rescue tab in EPD Commerce showing an Internal Fix First recovery strategy with retry cadence and email sequence
    caption: Order Rescue applies the same recovery strategy pattern to failed one-time orders.
---

# Revenue Recovery

## What it is

Revenue Recovery is the part of EPD Commerce that automatically retries failed payments and communicates with customers to rescue at-risk revenue. It covers both subscription payments (Recovery Templates) and one-time orders (Order Rescue).

When a payment fails, Revenue Recovery kicks in. It retries the transaction on the schedule the merchant configured, sends the customer the right message at the right time, and routes each recovery through a strategy matched to the reason the payment failed.

## How it works

Merchants set global rules once through **Retry & Communication Logic**: retry frequency, communication cadence, quiet hours, operating days, and campaign duration.

Every failed payment routes to a named strategy. Five ship out of the box:

- **Persistent Retry** for soft declines
- **Update Card First** for card data errors
- **Internal Fix First** for configuration and system issues
- **No Retry, Verify Required** for fraud and security declines
- **Switch Method & Notify** for account status issues

Merchants use them as shipped, edit them, or build their own from scratch.

**Optimized AI Strategy** is a toggle on every strategy. When active, EPD Commerce automatically routes each failed payment to the right strategy based on the decline reason. When off, the merchant controls routing.

**Order Rescue** applies the same five strategy patterns to failed one-time orders. Same recovery logic, different transaction type.

**Billing Notifications** handle customer-facing lifecycle emails (subscription activated, canceled, renewing soon, chargeback received, and more). **Email Templates** power every message the recovery campaigns send.

The **Revenue Recovery dashboard** shows total failed payments, revenue at risk, recovery rate, upcoming retries, and a filterable table of every failed transaction.

## How to talk about it

- Always capitalize: **Revenue Recovery**. Never "revenue recovery" mid-sentence, never "recovery" as shorthand.
- The related names are proper nouns and get their exact UI casing: **Recovery Templates**, **Order Rescue**, **Retry & Communication Logic**, **Billing Notifications**, **Email Templates**, **Optimized AI Strategy**.
- Attribute the behavior to the feature. "Revenue Recovery retries the payment." Not "our AI retries the payment."
- Especially relevant to subscription merchants. Lead with that when the audience is subscription-based.
- Never describe it as "dunning." That is industry jargon. Say "automatic retry" or "recovery" (in context).
