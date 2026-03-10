// Admin Dashboard JavaScript
let currentDonationId = null;

document.addEventListener('DOMContentLoaded', () => {
    // Search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', filterDonations);
    }
    
    // Delete team button handlers
    const deleteTeamButtons = document.querySelectorAll('.btn-delete-team');
    deleteTeamButtons.forEach(button => {
        button.addEventListener('click', function() {
            const teamId = this.getAttribute('data-team-id');
            const teamName = this.getAttribute('data-team-name');
            deleteTeam(teamId, teamName);
        });
    });
});

function filterDonations() {
    const searchInput = document.getElementById('searchInput').value.toLowerCase();
    const rows = document.querySelectorAll('#donationTableBody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchInput)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// ===== ADD TEAM MANAGEMENT =====
function openAddTeamModal() {
    document.getElementById('addTeamModal').classList.remove('hidden');
}

function closeAddTeamModal() {
    document.getElementById('addTeamModal').classList.add('hidden');
    document.getElementById('newTeamNameInput').value = '';
    document.getElementById('teamLeaderInput').value = '';
    document.getElementById('teamContactInput').value = '';
}

function createNewTeam() {
    const teamName = document.getElementById('newTeamNameInput').value.trim();
    const teamLeader = document.getElementById('teamLeaderInput').value.trim();
    const teamContact = document.getElementById('teamContactInput').value.trim();
    
    if (!teamName) {
        alert('Please enter a team name');
        return;
    }
    
    // Send to backend API
    fetch('/api/create-team/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            team_name: teamName,
            team_leader: teamLeader,
            team_contact: teamContact
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`✅ Team "${teamName}" has been created successfully!`);
            closeAddTeamModal();
            location.reload();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        alert('Network error. Please try again.');
        console.error('Error:', error);
    });
}

// ===== VERIFICATION WORKFLOW =====
function showVerifyModal(donationId) {
    currentDonationId = donationId;
    
    // Fetch donation details to show donor's food photo
    fetch(`/api/get-donation/${donationId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.food_photo) {
                document.getElementById('donorPhotoPreview').src = data.food_photo;
                document.getElementById('donorPhotoContainer').style.display = 'block';
            } else {
                document.getElementById('donorPhotoContainer').innerHTML = '<p style="color: #9ca3af;">No photo provided by donor</p>';
            }
        })
        .catch(error => console.error('Error fetching donation:', error));
    
    document.getElementById('verifyModal').classList.remove('hidden');
}

function closeVerifyModal() {
    document.getElementById('verifyModal').classList.add('hidden');
    // Reset form
    document.querySelectorAll('input[name="food_condition"]').forEach(el => el.checked = false);
    document.getElementById('adminNotesInput').value = '';
}

async function verifyAndApprove() {
    const foodCondition = document.querySelector('input[name="food_condition"]:checked');
    
    if (!foodCondition) {
        alert('Please select a food condition');
        return;
    }
    
    const adminNotes = document.getElementById('adminNotesInput').value.trim();
    
    try {
        // Verify the food condition (no file upload needed)
        let response = await fetch('/api/verify-food-condition/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                donation_id: currentDonationId,
                food_condition: foodCondition.value,
                admin_notes: adminNotes
            })
        });
        
        let data = await response.json();
        
        if (!data.success) {
            alert('Error verifying food: ' + data.message);
            return;
        }
        
        // Then approve the donation
        response = await fetch('/api/approve-donation/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                donation_id: currentDonationId
            })
        });
        
        data = await response.json();
        
        if (data.success) {
            alert('✅ Donation verified and approved successfully! Ready for team allocation.');
            closeVerifyModal();
            location.reload();
        } else {
            alert('Error approving donation: ' + data.message);
        }
    } catch (error) {
        alert('Network error. Please try again.');
        console.error('Error:', error);
    }
}

function showRejectModal() {
    closeVerifyModal();
    document.getElementById('rejectModal').classList.remove('hidden');
}

function closeRejectModal() {
    document.getElementById('rejectModal').classList.add('hidden');
    document.getElementById('rejectionReasonInput').value = '';
}

async function rejectDonation() {
    const rejectionReason = document.getElementById('rejectionReasonInput').value.trim();
    
    if (!rejectionReason) {
        alert('Please provide a reason for rejection');
        return;
    }
    
    try {
        const response = await fetch('/api/reject-donation/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                donation_id: currentDonationId,
                rejection_reason: rejectionReason
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('❌ Donation has been rejected.');
            closeRejectModal();
            location.reload();
        } else {
            alert('Error rejecting donation: ' + data.message);
        }
    } catch (error) {
        alert('Network error. Please try again.');
        console.error('Error:', error);
    }
}

// ===== ALLOCATION WORKFLOW =====
function showAllocateModal(donationId) {
    currentDonationId = donationId;
    document.getElementById('allocateModal').classList.remove('hidden');
}

function closeAllocateModal() {
    document.getElementById('allocateModal').classList.add('hidden');
    document.getElementById('allocateTeamInput').value = '';
}

async function allocateToTeam() {
    const team = document.getElementById('allocateTeamInput').value.trim();
    
    if (!team) {
        alert('Please enter a team name');
        return;
    }
    
    try {
        const response = await fetch('/api/allocate-to-team/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                donation_id: currentDonationId,
                team: team
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`✅ Donation allocated to ${team}! Ready for pickup.`);
            closeAllocateModal();
            location.reload();
        } else {
            alert('Error allocating donation: ' + data.message);
        }
    } catch (error) {
        alert('Network error. Please try again.');
        console.error('Error:', error);
    }
}

// ===== GENERAL EDIT =====
function editDonation(donationId) {
    currentDonationId = donationId;
    
    // Get row data
    const row = document.querySelector(`button[onclick*="${donationId}"]`).closest('tr');
    const cells = row.querySelectorAll('td');
    
    // Extract status from span (remove emojis and extra text)
    const statusSpan = cells[4].querySelector('.status-badge');
    const statusClass = statusSpan.className.split(' ')[1];
    
    // Populate form
    document.getElementById('statusSelect').value = statusClass;
    document.getElementById('teamInput').value = cells[6].textContent.replace('Not Assigned', '').trim();
    document.getElementById('locationInput').value = '';
    document.getElementById('peopleServedInput').value = '';
    document.getElementById('notesInput').value = '';
    
    // Show modal
    document.getElementById('editModal').classList.remove('hidden');
}

function closeEditModal() {
    document.getElementById('editModal').classList.add('hidden');
}

async function saveDonationEdit() {
    const status = document.getElementById('statusSelect').value;
    const team = document.getElementById('teamInput').value.trim();
    const location = document.getElementById('locationInput').value.trim();
    const peopleServed = parseInt(document.getElementById('peopleServedInput').value) || 0;
    const notes = document.getElementById('notesInput').value.trim();
    
    try {
        const response = await fetch('/api/update-status/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                donation_id: currentDonationId,
                status: status,
                team: team,
                location: location,
                people_served: peopleServed,
                notes: notes
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // If status is completed, regenerate report to capture updated location and people_served
            if (status === 'Completed') {
                try {
                    const reportResponse = await fetch('/api/generate-report/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            donation_id: currentDonationId
                        })
                    });
                    const reportData = await reportResponse.json();
                    if (reportData.success) {
                        alert('Donation updated and report regenerated with latest information!');
                    } else {
                        alert('Donation updated successfully!');
                    }
                } catch (error) {
                    alert('Donation updated successfully!');
                }
            } else {
                alert('Donation updated successfully!');
            }
            closeEditModal();
            // Update the stats counter immediately
            updateStatsCounter();
            // Then reload page after 500ms
            setTimeout(() => {
                location.reload();
            }, 500);
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        alert('Network error. Please try again.');
        console.error('Error:', error);
    }
}

// Function to update stats counter dynamically
async function updateStatsCounter() {
    try {
        const response = await fetch('/api/get-all-donations/');
        const data = await response.json();
        
        if (data.success) {
            // Count donations by status
            const donations = data.donations;
            const completed = donations.filter(d => d.status === 'completed').length;
            
            // Update the completed stat card
            const completedStatCard = document.querySelector('.stat-card:nth-child(3) .stat-value');
            if (completedStatCard) {
                completedStatCard.textContent = completed;
            }
        }
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// Delete Team Function
async function deleteTeam(teamId, teamName) {
    if (!confirm(`Are you sure you want to delete the team "${teamName}"?`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/delete-team/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                team_id: teamId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`✅ Team "${teamName}" has been deleted successfully!`);
            location.reload();
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        alert('Network error. Please try again.');
        console.error('Error:', error);
    }
}

// Generate Report Function
async function generateReport(donationId) {
    try {
        const response = await fetch('/api/generate-report/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                donation_id: donationId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Fetch and display the report
            getAndDisplayReport(donationId);
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        alert('Network error. Please try again.');
        console.error('Error:', error);
    }
}

// Get and Display Report
async function getAndDisplayReport(donationId) {
    try {
        const response = await fetch(`/api/get-report/?donation_id=${donationId}`);
        const data = await response.json();
        
        if (data.success) {
            const report = data.report;
            displayReportModal(report);
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        alert('Network error. Please try again.');
        console.error('Error:', error);
    }
}

// Display Report in Modal
function displayReportModal(report) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'reportModal';
    modal.innerHTML = `
        <div class="modal-content admin-modal" style="max-width: 600px;">
            <div class="modal-header">
                <h2>📋 Donation Report</h2>
                <button type="button" class="modal-close" onclick="this.closest('.modal').remove()">×</button>
            </div>
            <div class="modal-body">
                <div class="report-section">
                    <h3>Donor Information</h3>
                    <p><strong>Name:</strong> ${report.donor_name}</p>
                    <p><strong>Food Type:</strong> ${report.food_type}</p>
                </div>
                
                <div class="report-section">
                    <h3>Distribution Details</h3>
                    <p><strong>Team:</strong> ${report.team_name || 'Not assigned'}</p>
                    <p><strong>Location:</strong> ${report.distribution_center || 'Not specified'}</p>
                    <p><strong>People Served:</strong> ${report.people_served}</p>
                </div>
                
                <div class="report-section">
                    <h3>Impact Summary</h3>
                    <p>${report.impact_summary}</p>
                </div>
                
                ${report.satisfaction_rating ? `
                <div class="report-section">
                    <h3>Satisfaction Rating</h3>
                    <p><strong>Rating:</strong> ${report.satisfaction_rating}/5 ⭐</p>
                </div>
                ` : ''}
                
                <div class="report-section">
                    <p style="color: #999; font-size: 12px;">Report Generated: ${new Date(report.report_date).toLocaleString()}</p>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-primary" onclick="printReport()">🖨️ Print Report</button>
                <button type="button" class="btn btn-secondary" onclick="this.closest('.modal').remove()">Close</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

// Print Report
function printReport() {
    window.print();
}


// Close modal when clicking outside
window.addEventListener('click', (event) => {
    const editModal = document.getElementById('editModal');
    const verifyModal = document.getElementById('verifyModal');
    const rejectModal = document.getElementById('rejectModal');
    const allocateModal = document.getElementById('allocateModal');
    const addTeamModal = document.getElementById('addTeamModal');
    
    if (event.target === editModal) {
        closeEditModal();
    }
    if (event.target === verifyModal) {
        closeVerifyModal();
    }
    if (event.target === rejectModal) {
        closeRejectModal();
    }
    if (event.target === allocateModal) {
        closeAllocateModal();
    }
    if (event.target === addTeamModal) {
        closeAddTeamModal();
    }
});
