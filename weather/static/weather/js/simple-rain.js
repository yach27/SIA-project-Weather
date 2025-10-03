// Simple Rain System (Fallback)
document.addEventListener('DOMContentLoaded', function() {
    // Create rain container
    const rainContainer = document.createElement('div');
    rainContainer.id = 'simple-rain';
    rainContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 20;
        overflow: hidden;
    `;
    document.body.appendChild(rainContainer);

    // Create rain drops
    function createRainDrop() {
        const drop = document.createElement('div');
        drop.style.cssText = `
            position: absolute;
            width: 2px;
            height: ${Math.random() * 20 + 15}px;
            background: linear-gradient(to bottom, #87CEEB, #4682B4, transparent);
            left: ${Math.random() * 100}%;
            top: -30px;
            animation: fall ${Math.random() * 2 + 1}s linear infinite;
            border-radius: 1px;
            box-shadow: 0 0 2px rgba(135, 206, 235, 0.5);
        `;

        rainContainer.appendChild(drop);

        // Remove after animation
        setTimeout(() => {
            if (drop.parentNode) {
                drop.parentNode.removeChild(drop);
            }
        }, 3000);
    }

    // Add CSS animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fall {
            0% {
                transform: translateY(-30px);
                opacity: 1;
            }
            100% {
                transform: translateY(100vh);
                opacity: 0.3;
            }
        }
    `;
    document.head.appendChild(style);

    // Create rain drops continuously
    setInterval(createRainDrop, 50);

    console.log('Simple rain system started');
});