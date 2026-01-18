# Security Audit Checklist

## 1. Authentication & Authorization

### Google OAuth
- [ ] OAuth flow uses HTTPS only
- [ ] Credentials stored in `.env`, never in code
- [ ] Service account has minimal required permissions
- [ ] Token refresh handled securely
- [ ] Failed auth attempts logged

### API Keys
- [ ] All API keys in `.env` file
- [ ] `.env` in `.gitignore`
- [ ] API keys never logged
- [ ] Keys validated before use
- [ ] Invalid keys handled gracefully

---

## 2. Input Validation

### User Inputs
- [ ] All form inputs sanitized
- [ ] XSS protection on text fields
- [ ] File upload restrictions (type, size)
- [ ] URL validation for external links
- [ ] Email validation
- [ ] No code execution from user input

### AI Prompts
- [ ] Prompt injection detection
- [ ] User content sanitized before AI processing
- [ ] AI output validated before display
- [ ] No system prompts exposed to users

---

## 3. Data Protection

### Sensitive Data
- [ ] Passwords never stored (use OAuth)
- [ ] API keys encrypted at rest
- [ ] PII identified and protected
- [ ] No credentials in logs
- [ ] No credentials in error messages

### Data Storage
- [ ] Google Sheets access scoped properly
- [ ] No sensitive data in sheet names
- [ ] Sheet permissions reviewed
- [ ] Data retention policy documented

---

## 4. API Security

### External API Calls
- [ ] All API calls use HTTPS
- [ ] Timeouts configured
- [ ] Rate limiting respected
- [ ] Error responses don't leak info
- [ ] API keys rotated regularly

---

## 5. Dependencies

### Python Packages
- [ ] Run `safety check` for vulnerabilities
- [ ] All packages pinned to versions
- [ ] Dependencies reviewed for security
- [ ] No deprecated packages
- [ ] Regular updates scheduled

---

## 6. Code Security

### Static Analysis
- [ ] Run `bandit` security linter
- [ ] No hardcoded secrets
- [ ] No SQL injection vectors
- [ ] No command injection vectors
- [ ] File paths validated

---

## 7. Deployment

### Environment
- [ ] Debug mode disabled in production
- [ ] Appropriate logging level
- [ ] Error messages user-friendly
- [ ] Stack traces not exposed
- [ ] HTTPS enforced

---

## Security Scanning Commands

```bash
# Dependency vulnerabilities
safety check

# Code security issues
bandit -r src/

# Secret detection
git secrets --scan

# Outdated packages
pip list --outdated
```
