(function () {
    var userToggle = document.getElementById("userMenuToggle");
    var userMenu = document.getElementById("userDropdownMenu");

    if (userToggle && userMenu) {
        userToggle.addEventListener("click", function (event) {
            event.stopPropagation();
            var open = userMenu.classList.toggle("open");
            userToggle.setAttribute("aria-expanded", open ? "true" : "false");
        });
    }

    document.addEventListener("click", function (event) {
        if (userMenu && userMenu.classList.contains("open")) {
            if (!userMenu.contains(event.target) && !userToggle.contains(event.target)) {
                userMenu.classList.remove("open");
                userToggle.setAttribute("aria-expanded", "false");
            }
        }
    });

    var mobileToggle = document.getElementById("mobileNavToggle");
    var navScroll = document.getElementById("appNavScroll");

    if (mobileToggle && navScroll) {
        mobileToggle.addEventListener("click", function (event) {
            event.stopPropagation();
            var open = navScroll.classList.toggle("mobile-open");
            mobileToggle.setAttribute("aria-expanded", open ? "true" : "false");
            var icon = mobileToggle.querySelector("i");
            if (icon) {
                icon.className = open ? "bi bi-x-lg" : "bi bi-list";
            }
        });
    }

    document.addEventListener("click", function (event) {
        if (navScroll && navScroll.classList.contains("mobile-open")) {
            if (!navScroll.contains(event.target) && mobileToggle && !mobileToggle.contains(event.target)) {
                navScroll.classList.remove("mobile-open");
                if (mobileToggle) {
                    mobileToggle.setAttribute("aria-expanded", "false");
                    var icon = mobileToggle.querySelector("i");
                    if (icon) {
                        icon.className = "bi bi-list";
                    }
                }
            }
        }
    });

    var path = window.location.pathname;
    document.querySelectorAll(".app-nav-link[href]").forEach(function (link) {
        var href = link.getAttribute("href");
        if (href && href !== "/" && path.startsWith(href)) {
            link.classList.add("active");
        }
    });
})();
