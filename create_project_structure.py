import os

BASE_DIR = "Shorts-AutoMation-Web-App"

STRUCTURE = {
    "backend": {
        "server.py": "",
        "requirements.txt": "",
        ".env": "",
        "config": {
            "__init__.py": "",
            "database.py": "",
            "settings.py": "",
            "constants.py": "",
        },
        "models": {
            "__init__.py": "",
            "user.py": "",
            "account.py": "",
            "video.py": "",
            "analytics.py": "",
            "schedule.py": "",
        },
        "routes": {
            "__init__.py": "",
            "auth.py": "",
            "platforms.py": "",
            "content.py": "",
            "videos.py": "",
            "publish.py": "",
            "analytics.py": "",
            "dashboard.py": "",
            "insights.py": "",
        },
        "services": {
            "__init__.py": "",
            "auth_service.py": "",
            "content_generator.py": "",
            "tts_generator.py": "",
            "visual_generator.py": "",
            "video_renderer.py": "",
            "youtube_publisher.py": "",
            "instagram_publisher.py": "",
            "facebook_publisher.py": "",
            "analytics_sync.py": "",
            "insights_engine.py": "",
            "scheduler_service.py": "",
        },
        "middleware": {
            "__init__.py": "",
            "auth_middleware.py": "",
            "error_handler.py": "",
        },
        "utils": {
            "__init__.py": "",
            "jwt_utils.py": "",
            "encryption.py": "",
            "validators.py": "",
            "file_utils.py": "",
        },
        "workers": {
            "__init__.py": "",
            "render_worker.py": "",
            "scheduler_worker.py": "",
        },
        "storage": {
            "videos": {},
            "audio": {},
            "images": {},
            "temp": {},
        },
    },

    "frontend": {
        "src": {
            "index.js": "",
            "App.js": "",
            "App.css": "",
            "index.css": "",
            "components": {
                "ui": {
                    "button.jsx": "",
                    "card.jsx": "",
                    "input.jsx": "",
                    "select.jsx": "",
                },
                "layout": {
                    "Sidebar.jsx": "",
                    "Header.jsx": "",
                    "Layout.jsx": "",
                },
                "auth": {
                    "LoginForm.jsx": "",
                    "SignupForm.jsx": "",
                    "GoogleAuthButton.jsx": "",
                },
                "accounts": {
                    "AccountCard.jsx": "",
                    "ConnectButton.jsx": "",
                    "AccountsList.jsx": "",
                },
                "create": {
                    "ScriptGenerator.jsx": "",
                    "VoiceSelector.jsx": "",
                    "VisualSelector.jsx": "",
                    "VideoPreview.jsx": "",
                    "PublishModal.jsx": "",
                },
                "videos": {
                    "VideoCard.jsx": "",
                    "VideoList.jsx": "",
                    "VideoDetails.jsx": "",
                },
                "analytics": {
                    "SummaryCards.jsx": "",
                    "PlatformChart.jsx": "",
                    "PerformanceGraph.jsx": "",
                    "VideoMetricsTable.jsx": "",
                },
                "insights": {
                    "RecommendationCard.jsx": "",
                    "InsightsPanel.jsx": "",
                },
            },
            "pages": {
                "Login.jsx": "",
                "Signup.jsx": "",
                "Dashboard.jsx": "",
                "Accounts.jsx": "",
                "CreateVideo.jsx": "",
                "VideoLibrary.jsx": "",
                "Analytics.jsx": "",
            },
            "context": {
                "AuthContext.jsx": "",
                "AppContext.jsx": "",
            },
            "hooks": {
                "useAuth.js": "",
                "useApi.js": "",
                "use-toast.js": "",
            },
            "services": {
                "api.js": "",
            },
            "utils": {
                "constants.js": "",
                "helpers.js": "",
            },
        }
    }
}


def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)


if __name__ == "__main__":
    os.makedirs(BASE_DIR, exist_ok=True)
    create_structure(BASE_DIR, STRUCTURE)
    print("✅ Project folder structure created successfully!")

