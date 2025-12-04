// Quick debug script - paste this in browser console to check login state
console.log('=== TWIN Login Debug ===');
console.log('Logged in:', localStorage.getItem('twin_user_logged_in'));
console.log('Email:', localStorage.getItem('twin_user_email'));
console.log('Username element exists:', !!document.getElementById('userBottomLeft'));
console.log('Username display element exists:', !!document.getElementById('userNameDisplay'));
console.log('Logout button exists:', !!document.getElementById('logoutBtnTop'));
console.log('Username element style:', document.getElementById('userBottomLeft')?.style.display);
console.log('Logout button style:', document.getElementById('logoutBtnTop')?.style.display);

// Try to show them manually
const userDiv = document.getElementById('userBottomLeft');
const logoutBtn = document.getElementById('logoutBtnTop');
if (userDiv) {
    userDiv.style.display = 'block';
    console.log('✓ Showed username div');
}
if (logoutBtn) {
    logoutBtn.style.display = 'block';
    console.log('✓ Showed logout button');
}
