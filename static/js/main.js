/**
 * TN SKILLS – Database Administration Back End – Oracle
 * Vehicle Service Management Database System
 * JavaScript: main.js
 */

document.addEventListener("DOMContentLoaded", function () {
    // ------------------------------------------------------------------------
    // 1. Mobile Sidebar Toggle
    // ------------------------------------------------------------------------
    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("sidebar");

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener("click", function () {
            sidebar.classList.toggle("open");
        });

        // Close sidebar on document click outside
        document.addEventListener("click", function (e) {
            if (
                sidebar.classList.contains("open") &&
                !sidebar.contains(e.target) &&
                e.target !== sidebarToggle
            ) {
                sidebar.classList.remove("open");
            }
        });
    }

    // ------------------------------------------------------------------------
    // 2. Open Modal via URL Hash
    // ------------------------------------------------------------------------
    if (window.location.hash === "#addModal") {
        const defaultModals = [
            "addCustomerModal",
            "addVehicleModal",
            "addServiceModal"
        ];
        for (const mId of defaultModals) {
            const el = document.getElementById(mId);
            if (el) {
                openModal(mId);
                break;
            }
        }
    }

    // ------------------------------------------------------------------------
    // 3. Close Modals on ESC Key or Outside Click
    // ------------------------------------------------------------------------
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            const openModals = document.querySelectorAll(".modal-backdrop.open");
            openModals.forEach((m) => m.classList.remove("open"));
        }
    });

    const modalBackdrops = document.querySelectorAll(".modal-backdrop");
    modalBackdrops.forEach((backdrop) => {
        backdrop.addEventListener("click", function (e) {
            if (e.target === backdrop) {
                backdrop.classList.remove("open");
            }
        });
    });

    // ------------------------------------------------------------------------
    // 4. Auto Format Vehicle Number Input to Uppercase
    // ------------------------------------------------------------------------
    const regInputs = document.querySelectorAll("input[name='vehicle_number']");
    regInputs.forEach((input) => {
        input.addEventListener("input", function () {
            this.value = this.value.toUpperCase().replace(/\s+/g, "");
        });
    });

    // ------------------------------------------------------------------------
    // 5. Client-Side Form Validations
    // ------------------------------------------------------------------------
    const addCustomerForm = document.getElementById("addCustomerForm");
    if (addCustomerForm) {
        addCustomerForm.addEventListener("submit", function (e) {
            const contactInput = document.getElementById("contact_number");
            if (contactInput && !/^[0-9]{10}$/.test(contactInput.value.trim())) {
                e.preventDefault();
                alert("Validation Error: Contact number must be exactly 10 digits.");
                contactInput.focus();
                return false;
            }
        });
    }

    const addServiceForm = document.getElementById("addServiceForm");
    if (addServiceForm) {
        addServiceForm.addEventListener("submit", function (e) {
            const costInput = document.getElementById("service_cost");
            if (costInput && parseFloat(costInput.value) < 0) {
                e.preventDefault();
                alert("Validation Error: Service cost cannot be negative (Oracle CHECK constraint).");
                costInput.focus();
                return false;
            }
        });
    }
});

// ----------------------------------------------------------------------------
// Global Modal Helper Functions
// ----------------------------------------------------------------------------
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add("open");
        const firstInput = modal.querySelector("input:not([type=hidden]), select");
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove("open");
    }
}
