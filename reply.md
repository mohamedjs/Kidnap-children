## File Upload & FormData Issues Identified

### Root Causes Found

After investigating the frontend code, I found **two critical issues**:

#### Issue 1: FormData Reuse & Accumulation (Primary Cause of 422 Errors)
In `HomeComponent.vue` line 456 and `add_comment()` method (line 527-559):

```javascript
// In data()
data: new FormData(),  // Initialized once at component creation

// In create_post() / add_comment()
this.data.append('age', this.post.age);  // Appends to SAME FormData
```

**Problem**: FormData object is created once and reused forever. Each form submission **appends** new fields without clearing old ones.

**Cascade Effect**:
1. First submission: FormData has {name, gender, age, description, ...}
2. If clicked again OR if error occurs: Same FormData now has duplicates
3. Validation fails because fields appear multiple times
4. HTTP 422 error occurs

#### Issue 2: No Validation Error Reset
In the error handlers (lines 636-639 and similar):

```javascript
.catch(error => {
  _this.loading_posts_result = false;
  console.log(error);  // ERROR DATA STAYS IN FormData!
});
```

**Problem**: When HTTP 422 error occurs, the FormData is NOT reset. Next submission contains both old AND new data.

#### Issue 3: Double-Click / Race Condition
The submit button (line 166) has `disabled` state, but:
- If user clicks twice rapidly, second click may execute before first response completes
- Both calls append to the same FormData
- Server receives malformed request with duplicate fields

---

## Solution

Fix the FormData handling by:

1. **Create fresh FormData for each submission** (not once at component init)
2. **Reset FormData in ALL code paths** (success AND error)
3. **Reset file input after successful submission**
4. **Add form validation** to prevent empty submissions
5. **Ensure button stays disabled** during request

### Changes Needed

**In HomeComponent.vue**:
- Move `data: new FormData()` creation into `create_post()` method
- Reset after both success and error
- Clear file input element after submission
- Reset form fields after successful submission

**In components with comments**:
- Move FormData creation into `add_comment()` method  
- Ensure reset on both success and error paths

### Why This Fixes Your Issues

✅ No more field duplication in requests
✅ 422 validation errors will disappear
✅ Form data won't accumulate from failed submissions
✅ Double-click won't create duplicate requests
✅ Clean separation between requests

**Implementation**: Fix will be committed shortly.
