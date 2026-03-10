// Wait for DOM to be fully loaded before attaching event listeners
document.addEventListener('DOMContentLoaded', function() {
    const donationForm = document.getElementById('donationForm');
    
    if (!donationForm) {
        console.error('ERROR: donationForm element not found!');
        return;
    }
    
    console.log('✅ Form found and attaching submit listener');
    
    donationForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log('📝 Form submitted');
        
        // Get form data
        const fullName = document.getElementById('fullName').value.trim();
        const contNo = document.getElementById('contactNo').value.trim();
        const foodType = document.getElementById('foodType').value.trim();
        const preparationTime = document.getElementById('preparationTime').value.trim();
        const foodPhoto = document.getElementById('foodPhoto').files[0];
        const cdt = document.getElementById('cookingDateTime').value.trim();
        const pdt = document.getElementById('pickupDateTime').value.trim();
        const ploc = document.getElementById('pickupLocation').value.trim();
        
        console.log('📋 Form data captured:', {
            fullName, contNo, foodType, preparationTime, 
            foodPhoto: foodPhoto ? foodPhoto.name : 'none',
            cdt, pdt, ploc
        });
        
        // Validation
        if (!validateForm(fullName, contNo, foodType, preparationTime, foodPhoto, cdt, pdt, ploc)) {
            console.log('❌ Form validation failed');
            return;
        }
        
        console.log('✅ Form validation passed');
        
        try {
            // Create FormData for file upload
            const formData = new FormData();
            formData.append('full_name', fullName);
            formData.append('cont_no', contNo);
            formData.append('food_type', foodType);
            formData.append('preparation_time', preparationTime);
            formData.append('food_photo', foodPhoto);
            formData.append('cdt', cdt);
            formData.append('pdt', pdt);
            formData.append('ploc', ploc);
            
            console.log('📦 FormData contents:');
            for (let [key, value] of formData.entries()) {
                if (key === 'food_photo') {
                    console.log(`  ${key}: ${value.name} (${value.size} bytes, ${value.type})`);
                } else {
                    console.log(`  ${key}: ${value}`);
                }
            }
            
            console.log('🚀 Submitting to /api/submit-donation/...');
            
            // Submit form data
            const response = await fetch('/api/submit-donation/', {
                method: 'POST',
                body: formData
            });
            
            console.log(`📡 Response status: ${response.status}`);
            const data = await response.json();
            
            console.log('📥 Server response:', data);
            
            if (data.success) {
                // Show success modal
                document.getElementById('donationIdDisplay').textContent = data.donation_id;
                document.getElementById('successModal').classList.remove('hidden');
                
                // Reset form
                donationForm.reset();
                console.log('✅ Success! Form reset and modal shown.');
            } else {
                console.log('❌ Server returned error:', data.message);
                showErrorModal(data.message || 'An error occurred. Please try again.');
            }
        } catch (error) {
            console.error('❌ Fetch error:', error);
            showErrorModal('Network error. Please try again.');
        }
    });
});

function validateForm(fullName, contNo, foodType, preparationTime, foodPhoto, cdt, pdt, ploc) {
    const errors = {};
    
    if (!fullName || fullName.length === 0) {
        errors.fullName = 'Full name is required';
    }
    
    if (!contNo || contNo.length === 0) {
        errors.contNo = 'Contact number is required';
    } else {
        // Remove non-digits for validation
        const digitsOnly = contNo.replace(/\D/g, '');
        if (digitsOnly.length < 10) {
            errors.contNo = 'Please enter a valid phone number (at least 10 digits)';
        }
    }
    
    if (!foodType || foodType.length === 0) {
        errors.foodType = 'Food type is required';
    }
    
    if (!preparationTime || preparationTime.length === 0) {
        errors.preparationTime = 'Food preparation time is required';
    }
    
    if (!foodPhoto) {
        errors.foodPhoto = 'Food photo is required';
    } else if (!foodPhoto.type || !foodPhoto.type.startsWith('image/')) {
        errors.foodPhoto = 'Please upload a valid image file';
    }
    
    if (!cdt || cdt.length === 0) {
        errors.cdt = 'Cooking date & time is required';
    }
    
    if (!pdt || pdt.length === 0) {
        errors.pdt = 'Pickup date & time is required';
    }
    
    if (!ploc || ploc.length === 0) {
        errors.ploc = 'Pickup location is required';
    }
    
    // Check if pickup time is after cooking time
    if (cdt && pdt) {
        const cdtDate = new Date(cdt);
        const pdtDate = new Date(pdt);
        if (pdtDate <= cdtDate) {
            errors.pdt = 'Pickup time must be after cooking time';
        }
    }
    
    // Display errors
    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
    
    for (const [field, message] of Object.entries(errors)) {
        const fieldMap = {
            'contNo': 'contactNo',
            'preparationTime': 'preparationTime',
            'foodPhoto': 'foodPhoto'
        };
        const inputId = fieldMap[field] || field;
        const input = document.getElementById(inputId);
        if (input) {
            const errorEl = input.parentElement.querySelector('.error-message');
            if (errorEl) {
                errorEl.textContent = message;
            }
        }
    }
    
    // If there are errors, show them in console for debugging
    if (Object.keys(errors).length > 0) {
        console.log('Form validation errors:', errors);
    }
    
    return Object.keys(errors).length === 0;
}

function closeSuccessModal() {
    document.getElementById('successModal').classList.add('hidden');
    // Redirect to home after 2 seconds
    setTimeout(() => {
        window.location.href = '/';
    }, 500);
}

function closeErrorModal() {
    document.getElementById('errorModal').classList.add('hidden');
}

function showErrorModal(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorModal').classList.remove('hidden');
}

function copyDonationId() {
    const donationId = document.getElementById('donationIdDisplay').textContent;
    navigator.clipboard.writeText(donationId).then(() => {
        alert('Donation ID copied to clipboard!');
    }).catch(() => {
        alert('Failed to copy. Please copy manually.');
    });
}
