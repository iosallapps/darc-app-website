// darcapp.com: the before/after split and the one-time section fade. Nothing here is required
// to read the page; without this file the split stays at 50% and every section is visible.
(function () {
    "use strict";

    var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var NUDGE = 8;
    var NUDGE_MS = 450;

    function setupCompare(figure) {
        var screen = figure.querySelector(".screen");
        var range = figure.querySelector(".split-range");
        if (!screen || !range) { return; }

        // The range stops short of the edges so the 44px grip never slides under the frame.
        var low = Number(range.min) || 0;
        var high = Number(range.max) || 100;

        function show(value) {
            var clamped = Math.max(low, Math.min(high, value));
            screen.style.setProperty("--pos", clamped + "%");
            return clamped;
        }

        function setValue(value) {
            range.value = String(Math.round(show(value)));
            range.setAttribute("aria-valuetext", range.value + "% original, " + (100 - range.value) + "% with Darc");
        }

        range.addEventListener("input", function () { setValue(Number(range.value)); });

        var dragging = false;
        var startX = 0;
        var startY = 0;
        var decided = false;

        function valueAt(clientX) {
            var box = screen.getBoundingClientRect();
            return ((clientX - box.left) / box.width) * 100;
        }

        screen.addEventListener("pointerdown", function (event) {
            if (event.pointerType === "mouse" && event.button !== 0) { return; }
            dragging = true;
            decided = event.pointerType === "mouse";
            startX = event.clientX;
            startY = event.clientY;
            if (decided) {
                screen.setPointerCapture(event.pointerId);
                setValue(valueAt(event.clientX));
                event.preventDefault();
            }
        });

        screen.addEventListener("pointermove", function (event) {
            if (!dragging) { return; }
            if (!decided) {
                var dx = Math.abs(event.clientX - startX);
                var dy = Math.abs(event.clientY - startY);
                if (dx < 6 && dy < 6) { return; }
                if (dy > dx) { dragging = false; return; }
                decided = true;
                try { screen.setPointerCapture(event.pointerId); } catch (e) { /* already released */ }
            }
            setValue(valueAt(event.clientX));
        });

        function stop() { dragging = false; }
        screen.addEventListener("pointerup", stop);
        screen.addEventListener("pointercancel", stop);

        setValue(Number(range.value) || 50);

        if (reduceMotion || !("IntersectionObserver" in window) || !figure.hasAttribute("data-nudge")) { return; }
        var observer = new IntersectionObserver(function (entries) {
            if (!entries[0].isIntersecting) { return; }
            observer.disconnect();
            var base = Number(range.value);
            var start = null;
            function frame(now) {
                if (dragging) { return; }
                if (start === null) { start = now; }
                var t = Math.min(1, (now - start) / (NUDGE_MS * 2));
                show(base + Math.sin(t * Math.PI) * NUDGE);
                if (t < 1) { window.requestAnimationFrame(frame); } else { setValue(base); }
            }
            window.setTimeout(function () { window.requestAnimationFrame(frame); }, 400);
        }, { threshold: 0.6 });
        observer.observe(figure);
    }

    function setupReveal() {
        var items = document.querySelectorAll(".reveal");
        if (reduceMotion || !("IntersectionObserver" in window)) {
            for (var i = 0; i < items.length; i++) { items[i].classList.add("is-in"); }
            return;
        }
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-in");
                    observer.unobserve(entry.target);
                }
            });
        }, { rootMargin: "0px 0px -8% 0px" });
        for (var j = 0; j < items.length; j++) { observer.observe(items[j]); }
    }

    var figures = document.querySelectorAll(".compare");
    for (var k = 0; k < figures.length; k++) { setupCompare(figures[k]); }
    setupReveal();
})();
