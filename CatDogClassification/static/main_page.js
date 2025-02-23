// Pets information
const petsData = [
  {
    name: "Abyssinian",
    image:
      "https://images.pexels.com/photos/46024/pexels-photo-46024.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    description:
      "A well-muscled, strong, and athletic breed known for its confidence, loyalty, and excellent guardian instincts",
  },
  {
    name: "Bengal",
    image:
      "https://images.pexels.com/photos/46024/pexels-photo-46024.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    description:
      "An active, intelligent cat with a distinctive ticked tabby coat and graceful, athletic appearance",
  },
  {
    name: "Birman",
    image:
      "https://images.pexels.com/photos/46024/pexels-photo-46024.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    description:
      "A breed known for its strength, confidence, and strong desire to please their owners",
  },
  {
    name: "American Bulldog",
    image:
      "https://images.pexels.com/photos/46024/pexels-photo-46024.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    description:
      "A domestic cat breed developed to look like exotic wild cats, known for their distinctive spotted or marbled coat pattern",
  },
  {
    name: "American Pit Bull Terrier",
    image:
      "https://images.pexels.com/photos/46024/pexels-photo-46024.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    description:
      "A short-legged breed of dog with long ears, excellent scenting abilities, and a gentle, patient temperament",
  },
  {
    name: "Basset Hound",
    image:
      "https://images.pexels.com/photos/46024/pexels-photo-46024.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    description:
      "Known as the 'Sacred Cat of Burma', characterized by its silky coat, blue eyes, and white-gloved paws",
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
