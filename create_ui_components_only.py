import os

BASE_PATH = os.path.join(
    "Shorts-AutoMation-Web-App",
    "frontend",
    "src",
    "components",
    "ui"
)

UI_FILES = [
    "accordion.jsx",
    "alert-dialog.jsx",
    "alert.jsx",
    "aspect-ratio.jsx",
    "avatar.jsx",
    "badge.jsx",
    "breadcrumb.jsx",
    "button.jsx",
    "calendar.jsx",
    "card.jsx",
    "carousel.jsx",
    "checkbox.jsx",
    "collapsible.jsx",
    "command.jsx",
    "context-menu.jsx",
    "dialog.jsx",
    "drawer.jsx",
    "dropdown-menu.jsx",
    "form.jsx",
    "hover-card.jsx",
    "input-otp.jsx",
    "input.jsx",
    "label.jsx",
    "menubar.jsx",
    "navigation-menu.jsx",
    "pagination.jsx",
    "popover.jsx",
    "progress.jsx",
    "radio-group.jsx",
    "resizable.jsx",
    "scroll-area.jsx",
    "select.jsx",
    "separator.jsx",
    "sheet.jsx",
    "skeleton.jsx",
    "slider.jsx",
    "sonner.jsx",
    "switch.jsx",
    "table.jsx",
    "tabs.jsx",
    "textarea.jsx",
    "toast.jsx",
    "toaster.jsx",
    "toggle-group.jsx",
    "toggle.jsx",
    "tooltip.jsx",
    "ProtectedRoute.jsx"
]

def create_ui_files():
    os.makedirs(BASE_PATH, exist_ok=True)

    created = []
    skipped = []

    for file_name in UI_FILES:
        file_path = os.path.join(BASE_PATH, file_name)
        if os.path.exists(file_path):
            skipped.append(file_name)
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("")
            created.append(file_name)

    print("✅ UI folder setup complete\n")

    if created:
        print("🟢 Created files:")
        for f in created:
            print("  -", f)

    if skipped:
        print("\n🟡 Skipped (already existed):")
        for f in skipped:
            print("  -", f)


if __name__ == "__main__":
    create_ui_files()
