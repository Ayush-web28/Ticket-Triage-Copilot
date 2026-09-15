# Password Reset & Account Lockouts

If a customer is locked out or forgot their password:
1. Direct them to the "Forgot password" link on the login page; a reset email arrives within 2 minutes.
2. Reset links expire after 30 minutes -- if expired, have them request a new one.
3. If they don't receive the email, check they're not searching spam/junk, and confirm the email on file matches their account.
4. After 5 failed login attempts, accounts lock for 15 minutes automatically. This is not a manual block and clears itself.
5. For 2FA lockouts (lost authenticator device), verify identity via the account's recovery email, then send a one-time 2FA-reset link. Never disable 2FA over chat/email without identity verification.
