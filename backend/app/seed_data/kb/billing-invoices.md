# Billing, Invoices & Refunds

- Invoices are generated on the 1st of each billing cycle and emailed automatically; customers can also download them from Settings > Billing > Invoice History.
- Duplicate charges: verify in the payment processor dashboard before refunding. Genuine duplicate charges are refunded in full within 5-7 business days.
- Refund policy: full refund within 14 days of a charge for annual plans; monthly plans are refunded on a pro-rated basis for the unused portion.
- If a customer was charged after cancelling, check the cancellation timestamp against the renewal timestamp -- if cancellation came before renewal, it's a billing error and should be refunded immediately.
- Failed payments retry automatically 3 times over 7 days before a subscription is downgraded to the free tier.
