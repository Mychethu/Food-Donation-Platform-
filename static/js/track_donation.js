// Track Donation JavaScript
document.getElementById('trackBtn').addEventListener('click', trackDonation);
document.getElementById('donationIdInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        trackDonation();
    }
});

async function trackDonation() {
    const donationId = document.getElementById('donationIdInput').value.trim().toUpperCase();
    
    if (!donationId) {
        alert('Please enter a Donation ID');
        return;
    }
    
    try {
        const response = await fetch(`/api/track-donation/?donation_id=${donationId}`);
        const data = await response.json();
        
        if (data.success) {
            displayTrackingResult(data.donation);
        } else {
            document.getElementById('trackResult').classList.add('hidden');
            document.getElementById('notFoundMessage').classList.remove('hidden');
        }
    } catch (error) {
        alert('Error tracking donation. Please try again.');
        console.error('Error:', error);
    }
}

function displayTrackingResult(donation) {
    // Hide not found message, show result
    document.getElementById('notFoundMessage').classList.add('hidden');
    document.getElementById('trackResult').classList.remove('hidden');
    
    // Fill donation details
    document.getElementById('resId').textContent = donation.donation_id;
    document.getElementById('resName').textContent = donation.full_name;
    document.getElementById('resContact').textContent = donation.cont_no;
    document.getElementById('resFood').textContent = donation.food_type;
    document.getElementById('resLocation').textContent = donation.ploc;
    document.getElementById('resTeam').textContent = donation.team || 'Not Assigned';
    
    // Update status badge
    const statusDisplay = document.getElementById('statusDisplay');
    statusDisplay.innerHTML = '';
    const statusBadge = getStatusBadge(donation.status);
    statusDisplay.appendChild(statusBadge);
    
    // Update timeline
    updateTimeline(donation.status);
    
    // Show impact section if completed
    if (donation.status === 'completed' && donation.distribution) {
        document.getElementById('impactSection').style.display = 'block';
        document.getElementById('peopleServed').textContent = donation.distribution.people_served;
        document.getElementById('satisfaction').textContent = donation.distribution.satisfaction + '%';
        document.getElementById('center').textContent = donation.distribution.center;
    } else {
        document.getElementById('impactSection').style.display = 'none';
    }
}

function getStatusBadge(status) {
    const badge = document.createElement('div');
    badge.className = `status-badge ${status}`;
    
    const statusMap = {
        'pending': '⏳ Pending',
        'picked_up': '✓ Picked Up',
        'in_transit': '🚚 In Transit',
        'delivered': '📍 Delivered',
        'completed': '✅ Completed'
    };
    
    badge.textContent = statusMap[status] || 'Unknown';
    return badge;
}

function updateTimeline(status) {
    const statusOrder = ['pending', 'picked_up', 'in_transit', 'delivered', 'completed'];
    const currentIndex = statusOrder.indexOf(status);
    
    document.querySelectorAll('.timeline-item').forEach((item, index) => {
        item.classList.remove('completed', 'current');
        if (index < currentIndex) {
            item.classList.add('completed');
        } else if (index === currentIndex) {
            item.classList.add('current');
        }
    });
}

function resetTrack() {
    document.getElementById('donationIdInput').value = '';
    document.getElementById('trackResult').classList.add('hidden');
    document.getElementById('notFoundMessage').classList.add('hidden');
}
