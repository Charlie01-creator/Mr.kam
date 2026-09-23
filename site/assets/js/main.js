/* =========================================================
   Kamulegeya Mubarak Kiggundu — site config & behaviour
   ---------------------------------------------------------
   SITE CONFIG — edit these once real, verified contact
   details are supplied. Every page pulls from here, so this
   is the only file that needs updating.
   ========================================================= */
window.SITE = {
  // TODO: replace with the verified WhatsApp number, digits only,
  // in international format, e.g. "256700000000" for +256 700 000 000.
  whatsappNumber: "256000000000",
  // TODO: replace with the verified public contact email.
  contactEmail: "info@example.com",
  // TODO: replace with the verified public phone number (display format).
  contactPhoneDisplay: "+256 000 000 000",
};

document.addEventListener("DOMContentLoaded", function () {
  initMobileNav();
  initFaqAccordions();
  initSmartForms();
  markActiveNavLink();
  fillContactDetails();
});

/* ---------------- Contact detail placeholders ----------------
   Populates any element tagged data-contact="phone|email|whatsapp"
   from the single SITE config above, so contact details only ever
   need updating in one place. ---------------------------------- */
function fillContactDetails() {
  document.querySelectorAll('[data-contact="phone"]').forEach(function (el) {
    el.textContent = window.SITE.contactPhoneDisplay;
    if (el.tagName === "A") el.href = "tel:" + window.SITE.contactPhoneDisplay.replace(/\s+/g, "");
  });
  document.querySelectorAll('[data-contact="email"]').forEach(function (el) {
    el.textContent = window.SITE.contactEmail;
    if (el.tagName === "A") el.href = "mailto:" + window.SITE.contactEmail;
  });
  document.querySelectorAll('[data-contact="whatsapp"]').forEach(function (el) {
    if (el.tagName === "A") el.href = "https://wa.me/" + window.SITE.whatsappNumber;
  });
}

/* ---------------- Mobile nav ---------------- */
function initMobileNav() {
  var toggle = document.querySelector("[data-nav-toggle]");
  var drawer = document.querySelector("[data-mobile-nav]");
  if (!toggle || !drawer) return;

  function close() {
    drawer.classList.remove("open");
    toggle.setAttribute("aria-expanded", "false");
    document.body.style.overflow = "";
  }
  function open() {
    drawer.classList.add("open");
    toggle.setAttribute("aria-expanded", "true");
    document.body.style.overflow = "hidden";
  }

  toggle.addEventListener("click", function () {
    var isOpen = drawer.classList.contains("open");
    isOpen ? close() : open();
  });
  drawer.querySelectorAll("a").forEach(function (a) {
    a.addEventListener("click", close);
  });
  var closeBtn = drawer.querySelector("[data-nav-close]");
  if (closeBtn) closeBtn.addEventListener("click", close);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") close();
  });
}

/* ---------------- Active nav link ---------------- */
function markActiveNavLink() {
  var path = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".main-nav a, .mobile-nav a").forEach(function (a) {
    var href = a.getAttribute("href");
    if (href === path || (path === "" && href === "index.html")) {
      a.setAttribute("aria-current", "page");
    }
  });
}

/* ---------------- FAQ accordion ---------------- */
function initFaqAccordions() {
  document.querySelectorAll(".faq-item").forEach(function (item) {
    var btn = item.querySelector(".faq-q");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var isOpen = item.getAttribute("data-open") === "true";
      item.setAttribute("data-open", isOpen ? "false" : "true");
      btn.setAttribute("aria-expanded", isOpen ? "false" : "true");
    });
  });
}

/* ---------------- Forms: validation + WhatsApp/email handoff ----------------
   There is no backend configured yet, so submissions are not silently
   "sent" anywhere. Instead, once a form validates, we build a clear
   plain-text summary and hand it to the visitor via a pre-filled
   WhatsApp message (primary) and a pre-filled email draft (fallback),
   then show an on-page confirmation. This is a real, working flow today
   and is built so a proper backend/CRM can be dropped in later without
   changing the markup — see the comment at the bottom of this function.
------------------------------------------------------------------------ */
function initSmartForms() {
  document.querySelectorAll("form[data-smart-form]").forEach(function (form) {
    var confirmPanel = form.parentElement.querySelector("[data-confirm-panel]");

    form.addEventListener("submit", function (e) {
      e.preventDefault();

      var valid = true;
      var lines = [];
      var formTitle = form.getAttribute("data-form-title") || "New enquiry";

      form.querySelectorAll("[data-field]").forEach(function (field) {
        var errorEl = field.parentElement.querySelector(".field-error");
        var value = field.value ? field.value.trim() : "";
        var isRequired = field.hasAttribute("required");

        if (isRequired && !value) {
          valid = false;
          field.classList.add("invalid");
          if (errorEl) errorEl.textContent = "Please fill in this field.";
        } else if (field.type === "email" && value && !/^\S+@\S+\.\S+$/.test(value)) {
          valid = false;
          field.classList.add("invalid");
          if (errorEl) errorEl.textContent = "Please enter a valid email address.";
        } else {
          field.classList.remove("invalid");
        }

        if (value) {
          var label = field.getAttribute("data-label") || field.name;
          lines.push(label + ": " + value);
        }
      });

      if (!valid) {
        var firstInvalid = form.querySelector(".invalid");
        if (firstInvalid) firstInvalid.focus();
        return;
      }

      var message = formTitle + "%0A" + lines.map(encodeURIComponent).join("%0A");
      var waLink = "https://wa.me/" + window.SITE.whatsappNumber + "?text=" + message;
      var mailLink =
        "mailto:" + window.SITE.contactEmail +
        "?subject=" + encodeURIComponent(formTitle) +
        "&body=" + lines.map(encodeURIComponent).join("%0A");

      if (confirmPanel) {
        var waBtn = confirmPanel.querySelector("[data-wa-link]");
        var mailBtn = confirmPanel.querySelector("[data-mail-link]");
        if (waBtn) waBtn.setAttribute("href", waLink);
        if (mailBtn) mailBtn.setAttribute("href", mailLink);
        confirmPanel.classList.add("show");
        confirmPanel.setAttribute("tabindex", "-1");
        confirmPanel.focus();
        confirmPanel.scrollIntoView({ behavior: "smooth", block: "center" });
      }

      form.querySelectorAll("input, select, textarea, button").forEach(function (el) {
        el.disabled = true;
      });
    });
  });
}

/* ---------------------------------------------------------------
   WHEN A REAL BACKEND IS READY:
   Replace the body of the submit handler above with a fetch() call
   to your endpoint (or a form-backend service), keep the same
   validation block, and show confirmPanel on a successful response
   instead of building wa.me/mailto links. Nothing else on the page
   needs to change.
------------------------------------------------------------------- */

