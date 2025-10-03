// Weather Animation Scripts

class WeatherAnimations {
    constructor() {
        this.thunderInterval = null;
        this.isThunderActive = false;
        this.init();
    }

    init() {
        this.createThunderFlash();
        this.startThunderAnimation();
        this.addCloudHoverEffects();
        this.createFloatingElements();
    }

    // Create thunder flash overlay
    createThunderFlash() {
        const thunderFlash = document.createElement('div');
        thunderFlash.className = 'thunder-flash';
        thunderFlash.id = 'thunderFlash';
        document.body.appendChild(thunderFlash);
    }

    // Thunder animation with random intervals
    startThunderAnimation() {
        const triggerThunder = () => {
            if (!this.isThunderActive) {
                this.triggerThunderFlash();
                this.playThunderSound();
            }

            // Random interval between 8-15 seconds
            const nextThunder = Math.random() * 7000 + 8000;
            setTimeout(triggerThunder, nextThunder);
        };

        // Start first thunder after 5 seconds
        setTimeout(triggerThunder, 5000);
    }

    // Trigger thunder flash effect
    triggerThunderFlash() {
        this.isThunderActive = true;
        const thunderFlash = document.getElementById('thunderFlash');

        if (thunderFlash) {
            thunderFlash.classList.add('active');

            // Remove the flash after animation
            setTimeout(() => {
                thunderFlash.classList.remove('active');
                this.isThunderActive = false;
            }, 300);
        }

        // Make lightning bolts more prominent during thunder
        this.enhanceLightning();
    }

    // Enhance lightning during thunder
    enhanceLightning() {
        const lightningElements = document.querySelectorAll('.lightning-bolt');
        lightningElements.forEach(lightning => {
            lightning.style.animation = 'lightningBolt 0.3s ease-out';

            setTimeout(() => {
                lightning.style.animation = 'lightning 2s ease-in-out infinite';
            }, 300);
        });
    }

    // Play thunder sound (optional - can be enabled if audio files are added)
    playThunderSound() {
        // Uncomment and add audio file if needed
        // const audio = new Audio('/static/weather/audio/thunder.mp3');
        // audio.volume = 0.3;
        // audio.play().catch(e => console.log('Audio play failed:', e));
    }

    // Add hover effects to clouds
    addCloudHoverEffects() {
        const clouds = document.querySelectorAll('.cloud-element');

        clouds.forEach(cloud => {
            cloud.addEventListener('mouseenter', () => {
                cloud.style.transform = 'scale(1.1) translateY(-5px)';
                cloud.style.transition = 'transform 0.3s ease';
            });

            cloud.addEventListener('mouseleave', () => {
                cloud.style.transform = 'scale(1) translateY(0)';
            });
        });
    }

    // Create floating elements (leaves, particles)
    createFloatingElements() {
        this.createFloatingLeaves();
        this.createWeatherParticles();
    }

    // Create floating leaves
    createFloatingLeaves() {
        const leafCount = 3;

        for (let i = 0; i < leafCount; i++) {
            const leaf = document.createElement('div');
            leaf.className = 'absolute w-3 h-3 bg-green-400 rounded-full floating-leaf opacity-60';
            leaf.style.left = Math.random() * 80 + 10 + '%';
            leaf.style.top = Math.random() * 60 + 20 + '%';
            leaf.style.animationDelay = Math.random() * 3 + 's';
            leaf.style.animationDuration = Math.random() * 3 + 6 + 's';

            document.querySelector('.weather-background').appendChild(leaf);
        }
    }

    // Create weather particles
    createWeatherParticles() {
        const particleCount = 5;

        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'absolute w-1 h-1 bg-white rounded-full opacity-40';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.top = Math.random() * 100 + '%';
            particle.style.animation = `float ${Math.random() * 2 + 4}s ease-in-out infinite`;
            particle.style.animationDelay = Math.random() * 2 + 's';

            document.querySelector('.weather-background').appendChild(particle);
        }
    }

    // Wind effect on elements
    addWindEffect() {
        const windElements = document.querySelectorAll('.wind-affected');

        setInterval(() => {
            windElements.forEach(element => {
                const intensity = Math.random() * 10 - 5; // -5 to 5
                element.style.transform = `translateX(${intensity}px)`;
            });
        }, 100);
    }

    // Seasonal weather changes
    changeSeasonalWeather(season) {
        const background = document.querySelector('.weather-background');

        switch(season) {
            case 'winter':
                this.addSnowEffect();
                break;
            case 'autumn':
                this.addFallingLeavesEffect();
                break;
            case 'spring':
                this.addBlossomEffect();
                break;
            case 'summer':
                this.addHeatShimmerEffect();
                break;
        }
    }

    // Add snow effect
    addSnowEffect() {
        const snowCount = 20;

        for (let i = 0; i < snowCount; i++) {
            const snowflake = document.createElement('div');
            snowflake.className = 'absolute w-2 h-2 bg-white rounded-full opacity-80';
            snowflake.style.left = Math.random() * 100 + '%';
            snowflake.style.animation = `rain ${Math.random() * 3 + 2}s linear infinite`;
            snowflake.style.animationDelay = Math.random() * 2 + 's';

            document.querySelector('.weather-background').appendChild(snowflake);
        }
    }
}

// Initialize weather animations when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const weatherAnimations = new WeatherAnimations();

    // Optional: Add keyboard controls for testing
    document.addEventListener('keydown', (e) => {
        if (e.key === 't' || e.key === 'T') {
            weatherAnimations.triggerThunderFlash();
        }
    });
});

// Export for potential use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WeatherAnimations;
}