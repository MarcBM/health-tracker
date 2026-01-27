/**
 * Generic Card Stack System
 * Simple cycling through multiple card layers on click/touch
 */

function nextCard(element) {
    const cards = element.querySelectorAll('.card-layer');
    const current = parseInt(element.dataset.current || '0');
    const next = (current + 1) % cards.length;
    
    // Remove active from current card
    cards[current].classList.remove('active');
    
    // Add active to next card
    cards[next].classList.add('active');
    
    // Update current index
    element.dataset.current = next;
}

// Initialize all card stacks when page loads
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.card-stack').forEach(stack => {
        const firstCard = stack.querySelector('.card-layer');
        if (firstCard) {
            firstCard.classList.add('active');
            stack.dataset.current = '0';
        }
    });
}); 