# Testing Guide for Credit Workflow Updates

## Summary of Changes

The credit assignment and claiming workflow has been updated as follows:

### 1. **Assignment (Create Credit) Changes**
- **BEFORE**: Only required items, reason, and date
- **AFTER**: Now also requires customer name and customer phone number

**Form Fields Added:**
- Customer Name (required text field)
- Customer Phone Number (required tel field)

**Backend Validation:**
- Validates that customer_name is not empty
- Validates that customer_phone is not empty
- Stores both fields in the database during credit creation

### 2. **Claiming Changes**
- **BEFORE**: Prompted for customer name and phone in a form when claiming
- **AFTER**: Simply confirms and claims the credit, using stored customer info

**UI Changes:**
- Removed the multi-step claim form with customer input fields
- Now shows a simple confirmation dialog: "Claim credit {code} for {customer_name}?"
- Customer name and phone are automatically displayed from the credit record

**Backend Changes:**
- No longer accepts customer_name and customer_phone parameters in claim request
- Retrieves customer_name from the existing credit record for the success message
- Only updates claimed_at, claimed_by, and claimed_by_user fields

### 3. **Search Enhancements**
- **BEFORE**: Search by credit code or phone number
- **AFTER**: Search by credit code, customer name, or phone number

**Search Functionality:**
- Added customer name to searchable fields
- Updated placeholder text to reflect all search options
- JavaScript filterCredits() function now checks customerName data attribute

### 4. **Display Changes**
- **BEFORE**: Customer info only shown on claimed credits
- **AFTER**: Customer name and phone displayed on ALL credits (active and claimed)

This makes it easy to verify customer details before claiming.

## Manual Testing Steps

To test these changes manually:

### Test 1: Create Credit with Customer Info
1. Login to the application
2. Select a store
3. Navigate to the "Create New Credit" section
4. Add items (e.g., "Widget", "Gadget")
5. Enter a reason (e.g., "Defective product")
6. **NEW**: Enter customer name (e.g., "John Smith")
7. **NEW**: Enter customer phone (e.g., "555-1234")
8. Click "Generate Credit Code"
9. Verify success message shows credit code
10. Verify the new credit appears with customer name and phone visible

### Test 2: Validation - Missing Customer Name
1. Try to create a credit without entering customer name
2. Verify error message: "Customer name is required"

### Test 3: Validation - Missing Customer Phone
1. Try to create a credit without entering customer phone
2. Verify error message: "Customer phone number is required"

### Test 4: Claim Credit (Simplified)
1. Find an active credit in the list
2. Note the customer name shown on the credit
3. Click the "Claim" button
4. **NEW**: Verify simple confirmation dialog appears: "Claim credit {CODE} for {NAME}?"
5. Click OK to confirm
6. Verify success message: "Credit {CODE} claimed successfully for {NAME}!"
7. Verify credit status changes to "CLAIMED"
8. Verify "Claimed By" and "Claimed At" fields are populated

### Test 5: Search by Customer Name
1. Create multiple credits with different customer names
2. Use the search box to search for a customer name
3. Verify only credits matching that name are displayed
4. Test partial matches (e.g., search "John" finds "John Smith")

### Test 6: Search by Phone Number
1. Create credits with different phone numbers
2. Search by phone number
3. Verify credits are filtered correctly

### Test 7: Search by Credit Code
1. Search for a specific credit code
2. Verify only that credit is displayed

### Test 8: Display Customer Info on Active Credits
1. Create a new credit with customer info
2. Before claiming, verify customer name and phone are visible on the credit tile
3. This allows staff to verify customer details before claiming

### Test 9: Unclaim Credit
1. Claim a credit
2. Click the "Unclaim" button
3. Verify credit returns to "active" status
4. **IMPORTANT**: Verify customer name and phone REMAIN on the credit (not cleared)
5. This is expected behavior - customer info is assigned at creation and persists

## Automated Tests

Run the test suite to verify all functionality:

```bash
python test_app.py
```

The test suite includes:
- 8 tests for claim functionality (simplified without customer input)
- 8 tests for unclaim functionality
- 3 tests for create credit with customer info validation
- 3 tests for claiming without customer input
- Total: 25 tests

All tests should pass.

## Database Schema

The database already has customer_name and customer_phone columns in the credits table (added in a previous migration). No schema changes were needed for this update.

## Benefits of This Change

1. **Streamlined Claiming**: One-click claiming instead of multi-step form
2. **Data Integrity**: Customer info captured at assignment (when credit is created)
3. **Better Searchability**: Customers can locate credits by name if code is lost
4. **Improved Visibility**: Customer info visible on all credits, not just claimed ones
5. **Reduced Errors**: Customer info entered once, at creation, reducing duplicate entry errors
