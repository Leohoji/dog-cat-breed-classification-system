// Pets information
const petsData = [
  {
    name: "Abyssinian",
    image:
      "https://github.com/Leohoji/dog-cat-breed-classification-system/blob/main/Available_Breeds/Abyssinian.jpg?raw=true",
    description:
      "An active, playful cat known for its striking length, coat and stable social personality.",
  },
  {
    name: "Bengal",
    image:
      "https://github.com/Leohoji/dog-cat-breed-classification-system/blob/main/Available_Breeds/Bengal.jpg?raw=true",
    description:
      "An energetic cat with a wild appearance, featuring leopard-like spots and a playful, affectionate nature.",
  },
  {
    name: "Birman",
    image:
      "https://github.com/Leohoji/dog-cat-breed-classification-system/blob/main/Available_Breeds/Birman.jpg?raw=true",
    description:
      "A gentle, affectionate cats distinguished by their striking blue eyes and soft, silky fur.",
  },
  {
    name: "American Bulldog",
    image:
      "https://github.com/Leohoji/dog-cat-breed-classification-system/blob/main/Available_Breeds/american_bulldog.jpg?raw=true",
    description:
      "A strong, loyal breed known for its protective nature and friendly demeanor towards families.",
  },
  {
    name: "American Pit Bull Terrier",
    image:
      "https://github.com/Leohoji/dog-cat-breed-classification-system/blob/main/Available_Breeds/american_pit_bull_terrier.jpg?raw=true",
    description:
      "A breed is known for its strength and intelligence, often characterized by loyalty and a playful attitude.",
  },
  {
    name: "Basset Hound",
    image:
      "https://github.com/Leohoji/dog-cat-breed-classification-system/blob/main/Available_Breeds/basset_hound.jpg?raw=true",
    description:
      "A laid-back, friendly dog with long ears and a keen sense of smell, making them excellent scent hounds.",
  },
];

// Generate pet card HTML
function createPetCard(pet) {
  return `
        <div class="species-card">
            <img src="${pet.image}" alt="${pet.name}" class="species-image" loading="lazy" />
            <div class="species-details">
                <div class="species-name">${pet.name}</div>
                <div class="species-description">${pet.description}</div>
            </div>
        </div>
    `;
}

// Load all pet cards
function loadPetCards() {
  const speciesGrid = document.querySelector(".species-grid");
  if (speciesGrid) {
    const cardsHTML = petsData.map(createPetCard).join("");
    speciesGrid.innerHTML = cardsHTML;
  }
}

// Carousel functionality
function initializeCarousel() {
  // Get necessary DOM elements
  const carousel = document.querySelector(".carousel");
  const items = document.querySelectorAll(".carousel-item");
  const dots = document.querySelectorAll(".dot");
  const prevBtn = document.querySelector("#prevBtn");
  const nextBtn = document.querySelector("#nextBtn");

  if (!carousel || !items.length) return;

  let currentIndex = 0;
  const totalItems = items.length;
  let autoPlayTimer = setInterval(nextSlide, 5000);

  // Update carousel position and state
  function updateCarousel() {
    carousel.style.transform = `translateX(-${currentIndex * 100}%)`;

    // Update navigation dots state
    dots.forEach((dot, index) => {
      dot.classList.toggle("active", index === currentIndex);
    });

    // Reset auto-play timer
    clearInterval(autoPlayTimer);
    autoPlayTimer = setInterval(nextSlide, 5000);
  }

  // Next slide
  function nextSlide() {
    currentIndex = (currentIndex + 1) % totalItems;
    updateCarousel();
  }

  // Previous slide
  function prevSlide() {
    currentIndex = (currentIndex - 1 + totalItems) % totalItems;
    updateCarousel();
  }

  // Event listeners setup
  prevBtn.addEventListener("click", prevSlide);
  nextBtn.addEventListener("click", nextSlide);

  // Click navigation dots to switch
  dots.forEach((dot, index) => {
    dot.addEventListener("click", () => {
      currentIndex = index;
      updateCarousel();
    });
  });

  // Pause auto-play on mouse hover
  carousel.addEventListener("mouseenter", () => {
    clearInterval(autoPlayTimer);
  });

  carousel.addEventListener("mouseleave", () => {
    autoPlayTimer = setInterval(nextSlide, 5000);
  });
}

// Execute after DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
  // Initialize carousel
  initializeCarousel();

  // Load pet cards
  loadPetCards();

  // -------------------------------
  // Login button event handler
  // -------------------------------
  const loginBtn = document.getElementById("loginBtn");
  if (loginBtn) {
    loginBtn.addEventListener("click", () => {
      window.location.href = "/login/";
    });
  }

  // -------------------------------
  // Signup button event handler
  // -------------------------------
  const signupBtn = document.getElementById("signupBtn");
  if (signupBtn) {
    signupBtn.addEventListener("click", () => {
      window.location.href = "/signup/";
    });
  }
});
