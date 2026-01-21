# Production Deployment - Testing Checklist
**Site:** https://ipv.snpdemo.com
**Date:** ___________
**Tester:** ___________

---

## Pre-Deployment

- [ ] Backup current database
  ```bash
  docker compose -f docker-compose.prod.yml exec db pg_dump -U postgres defect_system > backup_$(date +%Y%m%d).sql
  ```

- [ ] Verify current git status
  ```bash
  git status
  git log --oneline -5
  ```

- [ ] Note current commit hash: ___________

---

## Deployment

- [ ] Pull latest code
  ```bash
  git pull origin main
  ```

- [ ] Verify changes are present
  ```bash
  git diff HEAD~1 backend/app/api/endpoints/auth.py
  git diff HEAD~1 frontend/nginx.conf
  ```

- [ ] Rebuild containers
  ```bash
  docker compose -f docker-compose.prod.yml build frontend backend
  ```

- [ ] Restart services
  ```bash
  docker compose -f docker-compose.prod.yml up -d --no-deps frontend backend
  ```

- [ ] Check container status
  ```bash
  docker compose -f docker-compose.prod.yml ps
  ```
  **Expected:** All containers "Up" status

- [ ] Check logs for errors
  ```bash
  docker compose -f docker-compose.prod.yml logs backend --tail 50 | grep -i error
  ```
  **Expected:** No critical errors

---

## Test #1: Authentication (BUG 1 Fix)

**Goal:** Verify /api/auth/me returns user object, not DB session

- [ ] **Step 1:** Open browser DevTools (F12) → Network tab

- [ ] **Step 2:** Go to https://ipv.snpdemo.com

- [ ] **Step 3:** Login with admin credentials
  - Username: ___________
  - Password: ___________

- [ ] **Step 4:** Check Network tab for `/api/auth/me` request
  - **Status:** ⬜ 200 OK  ⬜ Other: ___________
  - **Response:** ⬜ User object with id/username/email  ⬜ Error

- [ ] **Step 5:** Go to https://ipv.snpdemo.com/defects
  - **Result:** ⬜ Page loads  ⬜ 500 error  ⬜ Other: ___________

- [ ] **Step 6:** Check browser console (F12 → Console)
  - **Errors:** ⬜ None  ⬜ Yes (describe): ___________

**Pass Criteria:** ✅ Page loads, no 500 errors, user object returned

**Status:** ⬜ PASS  ⬜ FAIL  ⬜ SKIP

**Notes:** ___________________________________________

---

## Test #2: Defect List Page

**Goal:** Verify profiles load without errors

- [ ] **Step 1:** On /defects page, verify profiles are visible
  - **Count:** _____ profiles displayed

- [ ] **Step 2:** Check if OK profiles show green checkmark
  - **Result:** ⬜ Yes  ⬜ No OK profiles exist  ⬜ Not showing correctly

- [ ] **Step 3:** Click on a profile image thumbnail
  - **Result:** ⬜ Opens full-size image  ⬜ Error

- [ ] **Step 4:** Check logs
  ```bash
  docker compose -f docker-compose.prod.yml logs backend --tail 20
  ```
  - **Log shows:** ⬜ "User X fetching defect profiles"
  - **Log shows:** ⬜ "Returning X defect profiles"

**Pass Criteria:** ✅ All profiles load, images display correctly

**Status:** ⬜ PASS  ⬜ FAIL  ⬜ SKIP

**Notes:** ___________________________________________

---

## Test #3: Create Profile - Normal Upload (BUG 2 Fix)

**Goal:** Verify 413 error is fixed for reasonable uploads

- [ ] **Step 1:** Prepare test images
  - **Files:** 3-5 images, ~2-5MB each
  - **Total size:** ~_____ MB (should be < 50MB)

- [ ] **Step 2:** Go to Create Defect Profile page

- [ ] **Step 3:** Fill in form
  - Customer: ___________
  - Product: ___________
  - Defect type: ___________
  - Upload images: (select prepared files)

- [ ] **Step 4:** Submit form
  - **Result:** ⬜ Success  ⬜ 413 error  ⬜ Other: ___________
  - **Message:** ___________________________________________

- [ ] **Step 5:** If success, verify profile appears in list
  - **Result:** ⬜ Appears  ⬜ Not showing  ⬜ Error

**Pass Criteria:** ✅ Profile created successfully, no 413 error

**Status:** ⬜ PASS  ⬜ FAIL  ⬜ SKIP

**Notes:** ___________________________________________

---

## Test #4: Create Profile - Large Image (Validation)

**Goal:** Verify backend validation returns clear error

- [ ] **Step 1:** Prepare one large test image
  - **File size:** _____ MB (should be > 10MB)

- [ ] **Step 2:** Try to create profile with this image

- [ ] **Step 3:** Submit form
  - **Result:** ⬜ 400 error with clear message  ⬜ Success (bad!)  ⬜ Other: ___________
  - **Error message:** ___________________________________________

**Expected message:** "Image 1 (filename.jpg) is too large. Maximum size is 10MB per image."

**Pass Criteria:** ✅ Returns 400 with helpful error message

**Status:** ⬜ PASS  ⬜ FAIL  ⬜ SKIP

**Notes:** ___________________________________________

---

## Test #5: Create Profile - Too Many Images (Validation)

**Goal:** Verify max image limit enforcement

- [ ] **Step 1:** Prepare 25 small test images

- [ ] **Step 2:** Try to create profile with all 25 images

- [ ] **Step 3:** Submit form
  - **Result:** ⬜ 400 error  ⬜ Success (bad!)  ⬜ Other: ___________
  - **Error message:** ___________________________________________

**Expected message:** "Too many images. Maximum 20 images allowed per profile."

**Pass Criteria:** ✅ Returns 400 with helpful error message

**Status:** ⬜ PASS  ⬜ FAIL  ⬜ SKIP

**Notes:** ___________________________________________

---

## Test #6: Update User Password (BUG 3 Fix)

**Goal:** Verify password update works (UUID fix)

- [ ] **Step 1:** Go to User Management page

- [ ] **Step 2:** Select a non-admin test user to edit
  - **Username:** ___________
  - **Current UUID:** ___________

- [ ] **Step 3:** Click Edit button

- [ ] **Step 4:** Enter new password
  - **New password:** ___________ (remember this!)

- [ ] **Step 5:** Submit form
  - **Result:** ⬜ Success  ⬜ 404 error  ⬜ Other: ___________
  - **Message:** ___________________________________________

**Expected message:** "Cập nhật người dùng thành công"

- [ ] **Step 6:** Logout and try logging in as edited user
  - **Result:** ⬜ Login success  ⬜ Login failed  ⬜ Error

**Pass Criteria:** ✅ Password updated successfully, can login with new password

**Status:** ⬜ PASS  ⬜ FAIL  ⬜ SKIP

**Notes:** ___________________________________________

---

## Test #7: Update User - Blank Password (Regression)

**Goal:** Verify leaving password blank still works

- [ ] **Step 1:** Edit same test user again

- [ ] **Step 2:** Leave password field BLANK

- [ ] **Step 3:** Change another field (e.g., full name)
  - **New name:** ___________

- [ ] **Step 4:** Submit form
  - **Result:** ⬜ Success  ⬜ Error

- [ ] **Step 5:** Try logging in with OLD password
  - **Result:** ⬜ Login success (good!)  ⬜ Login failed (bad!)

**Pass Criteria:** ✅ User updated, password unchanged

**Status:** ⬜ PASS  ⬜ FAIL  ⬜ SKIP

**Notes:** ___________________________________________

---

## Test #8: Create OK Profile (UX Verification)

**Goal:** Verify OK/No Defect profile creation works

- [ ] **Step 1:** Go to Create Defect Profile

- [ ] **Step 2:** Select defect type dropdown
  - **Shows:** ⬜ "✅ OK / No Defect" option  ⬜ Not showing

- [ ] **Step 3:** Select "✅ OK / No Defect"
  - **Helper text shows:** ⬜ "Upload ảnh sản phẩm BÌNH THƯỜNG (không có lỗi)"
  - **Upload button text:** ⬜ Green color, mentions "BÌNH THƯỜNG"

- [ ] **Step 4:** Upload 3 normal (non-defect) images

- [ ] **Step 5:** Fill in other fields, submit
  - **Result:** ⬜ Success  ⬜ Error

- [ ] **Step 6:** Go to /defects list
  - **OK profile shows:** ⬜ Green checkmark "✅ OK"
  - **Severity shows:** ⬜ "Không có lỗi" (green badge)

**Pass Criteria:** ✅ OK profile created and displays correctly

**Status:** ⬜ PASS  ⬜ FAIL  ⬜ SKIP

**Notes:** ___________________________________________

---

## Test #9: Logging Verification

**Goal:** Verify defensive logging is working

- [ ] **Step 1:** Trigger any action (e.g., load defect list)

- [ ] **Step 2:** Check backend logs
  ```bash
  docker compose -f docker-compose.prod.yml logs backend --tail 30
  ```

- [ ] **Step 3:** Verify log entries
  - **Shows:** ⬜ "User X fetching defect profiles"
  - **Shows:** ⬜ "Returning X defect profiles"
  - **Shows:** ⬜ "Creating defect profile with X images" (if created profile)
  - **No secrets:** ⬜ No passwords/tokens in logs

**Pass Criteria:** ✅ Informative logs, no secrets leaked

**Status:** ⬜ PASS  ⬜ FAIL  ⬜ SKIP

**Notes:** ___________________________________________

---

## Post-Deployment Monitoring

- [ ] **5 minutes:** Monitor logs for errors
  ```bash
  docker compose -f docker-compose.prod.yml logs -f backend
  ```

- [ ] **10 minutes:** Check container resource usage
  ```bash
  docker stats --no-stream
  ```

- [ ] **15 minutes:** Verify no crashes
  ```bash
  docker compose -f docker-compose.prod.yml ps
  ```

**Any issues?** ⬜ No  ⬜ Yes (describe): ___________

---

## Final Sign-Off

**Total Tests:** 9
**Passed:** _____
**Failed:** _____
**Skipped:** _____

**Overall Status:** ⬜ SUCCESS  ⬜ PARTIAL  ⬜ FAILED

**Action Required:** ⬜ None  ⬜ Fix issues  ⬜ ROLLBACK

**Rollback Executed:** ⬜ N/A  ⬜ Yes  ⬜ No

---

## Rollback Commands (if needed)

```bash
# Stop services
docker compose -f docker-compose.prod.yml down

# Rollback code
git reset --hard <previous-commit-hash>

# Rebuild and restart
docker compose -f docker-compose.prod.yml up -d --build

# Verify
curl -I https://ipv.snpdemo.com/health
docker compose -f docker-compose.prod.yml ps
```

**Rollback Commit Hash:** ___________

---

**Deployment Completed By:** ___________
**Date:** ___________
**Time:** ___________
**Signature:** ___________

---

**Next Steps:**
- [ ] Archive this checklist
- [ ] Update deployment log
- [ ] Notify team of deployment status
- [ ] Schedule follow-up check (24 hours)

---

**Notes / Issues Encountered:**

___________________________________________________________

___________________________________________________________

___________________________________________________________

___________________________________________________________
