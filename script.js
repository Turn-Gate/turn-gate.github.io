document.addEventListener("DOMContentLoaded", function () {
    // Mobile Nav Toggle
    const navToggle = document.querySelector(".nav-toggle");
    const sideNav = document.querySelector(".sidebar-nav");
    const mobileHeader = document.querySelector(".mobile-header");

    const closeMobileNav = () => {
        if (!sideNav) return;
        sideNav.style.display = 'none';
        document.body.style.overflow = '';
        navToggle?.setAttribute('aria-expanded', 'false');
    };

    const openMobileNav = () => {
        if (!sideNav || !mobileHeader) return;
        sideNav.style.display = 'block';
        sideNav.style.position = 'fixed';
        sideNav.style.top = mobileHeader.offsetHeight + 'px';
        sideNav.style.left = '0';
        sideNav.style.width = '100%';
        sideNav.style.height = `calc(100vh - ${mobileHeader.offsetHeight}px)`;
        document.body.style.overflow = 'hidden';
        navToggle?.setAttribute('aria-expanded', 'true');
    };

    if (navToggle && sideNav) {
        navToggle.addEventListener("click", function () {
            if (window.innerWidth <= 900) {
                const isVisible = getComputedStyle(sideNav).display !== 'none';
                if (isVisible) {
                    closeMobileNav();
                } else {
                    openMobileNav();
                }
            }
        });
    }

    window.addEventListener('resize', () => {
        if (!sideNav) return;
        if (window.innerWidth > 900) {
            sideNav.removeAttribute('style');
            document.body.style.overflow = '';
            navToggle?.setAttribute('aria-expanded', 'false');
        } else if (navToggle?.getAttribute('aria-expanded') === 'true') {
            openMobileNav();
        }
    });

    // Active Link Highlighting
    const currentPath = window.location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll(".side-nav .nav-link").forEach(link => {
        const href = link.getAttribute("href");
        if (href === currentPath) {
            link.classList.add("is-active");
        } else {
            link.classList.remove("is-active");
        }
    });

    // Reveal animations on scroll
    const reveals = document.querySelectorAll(".reveal");
    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };

    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("is-visible");
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    reveals.forEach(el => revealObserver.observe(el));

    // Smooth scroll for internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Close mobile menu if open
                if (window.innerWidth <= 900) {
                    closeMobileNav();
                }
            }
        });
    });

    const motionFrame = document.getElementById("motion-iframe");
    if (motionFrame) {
        const updateMotionHeight = (height) => {
            const nextHeight = Number(height);
            if (!Number.isFinite(nextHeight) || nextHeight <= 0) return;
            motionFrame.style.height = `${Math.max(320, Math.round(nextHeight))}px`;
        };

        window.addEventListener("message", (event) => {
            if (event.source !== motionFrame.contentWindow) return;
            const data = event.data;
            if (!data || data.type !== "tg-iframe-height") return;
            updateMotionHeight(data.height);
        });
    }
});
