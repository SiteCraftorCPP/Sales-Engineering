/**
 * Lenis smooth scroll — якоря обрабатываются в index extra_js с учётом шапки и #audit/#contact
 */

function initSmoothScroll() {
    // 1. Initialize Lenis
    const lenis = new Lenis({
        duration: 1.2,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
        direction: 'vertical',
        gestureDirection: 'vertical',
        smooth: true,
        mouseMultiplier: 1,
        smoothTouch: false, // Native touch for mobile
        touchMultiplier: 2,
        infinite: false,
    });

    // Handle RequestAnimationFrame
    function raf(time) {
        lenis.raf(time);
        requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    // 2. Anchor links handled in index extra_js with header/audit/contact offsets

    // 3. Accessibility & Performance
    window.addEventListener('load', () => {
        lenis.resize();
    });

    // Expose to window for global access (e.g. stop/start on modals)
    window.lenis = lenis;
}

// Initial Run
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSmoothScroll);
} else {
    initSmoothScroll();
}
