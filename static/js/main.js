// Sectors & Price Ranges
const sectors = {
    "Dwarka": ["Sector 6 - Metro Connected", "Sector 10 - Family Hub", "Sector 12 - Commercial Center"],
    "Rohini": ["Sector 3 - Budget Friendly", "Sector 9 - Well Connected", "Sector 13 - Peaceful Area"],
    "Saket": ["Block A - Shopping District", "Block D - Residential Elite"],
    "Vasant Kunj": ["Sector A - Diplomatic Enclave", "Sector C - Premium Locality"],
    "Janakpuri": ["Block A1 - Metro Hub", "Block B2 - Family Zone"],
    "Karol Bagh": ["Main Market - Commercial Heart", "Ajmal Khan Road - Shopping Paradise"]
};

const locationPriceRanges = {
    "Dwarka": "₹85-95 Lakhs avg",
    "Rohini": "₹65-75 Lakhs avg", 
    "Saket": "₹1.2-1.8 Crores avg",
    "Vasant Kunj": "₹1.8-2.5 Crores avg",
    "Janakpuri": "₹90L-1.2 Crores avg",
    "Karol Bagh": "₹1.1-1.6 Crores avg"
};

// Update sector dropdown
function updateSectors() {
    const location = document.getElementById("location").value;
    const sectorSelect = document.getElementById("sector");
    sectorSelect.innerHTML = "<option value=''>Loading sectors...</option>";
    sectorSelect.disabled = true;

    setTimeout(() => {
        sectorSelect.innerHTML = "<option value=''>Choose specific sector...</option>";
        if (location && sectors[location]) {
            sectors[location].forEach(sec => {
                const option = document.createElement("option");
                option.value = sec.split(" - ")[0];
                option.text = sec;
                sectorSelect.appendChild(option);
            });
            if (locationPriceRanges[location]) showPriceHint(locationPriceRanges[location]);
        }
        sectorSelect.disabled = false;
    }, 300);
}

// Show price hint
function showPriceHint(priceRange) {
    const existingHint = document.querySelector('.price-hint');
    if (existingHint) existingHint.remove();

    const hint = document.createElement('div');
    hint.className = 'price-hint';
    hint.style.cssText = `
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.2);
        color: #60a5fa;
        padding: 10px 15px;
        border-radius: 8px;
        margin-top: 10px;
        font-size: 0.9rem;
        text-align: center;
        animation: fadeInUp 0.5s ease-out;
    `;
    hint.innerHTML = `💡 Average price range: <strong>${priceRange}</strong>`;
    const locationSection = document.querySelector('.form-section');
    locationSection.appendChild(hint);

    setTimeout(() => {
        if (hint.parentNode) {
            hint.style.opacity = '0';
            hint.style.transform = 'translateY(-10px)';
            setTimeout(() => hint.remove(), 300);
        }
    }, 5000);
}

// Optional: Add floating shape animations, smooth scroll, form validation, etc.
// Copy the rest of your JS from <script> in HTML except Voiceflow

document.addEventListener("DOMContentLoaded", () => {
    updateSectors(); // Optional initial call
});
