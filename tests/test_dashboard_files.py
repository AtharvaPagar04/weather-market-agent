import os

def test_dashboard_files_exist():
    expected_files = [
        "dashboard/streamlit_app.py",
        "dashboard/api_client.py",
        "dashboard/components.py",
        "dashboard/pages/__init__.py",
        "dashboard/pages/overview.py",
        "dashboard/pages/predictions.py",
        "dashboard/pages/risk_dashboard.py",
        "dashboard/pages/paper_trades.py",
        "dashboard/pages/agent_logs.py",
    ]
    for filepath in expected_files:
        assert os.path.exists(filepath), f"{filepath} is missing"

def test_streamlit_app_contains_page_config():
    with open("dashboard/streamlit_app.py", "r") as f:
        content = f.read()
    assert "st.set_page_config(" in content

def test_safety_banner_text_exists():
    with open("dashboard/components.py", "r") as f:
        content = f.read()
    assert "Paper trading only — all execution shown is simulated. No real funds, wallets, private keys, signing credentials, or real-money orders are used." in content

def test_no_forbidden_terms_except_safety_warning():
    forbidden_terms = ["wallet", "private_key", "SIGNING_CREDENTIAL", "FUNDED_ACCOUNT", "TRADING_ACCOUNT_SECRET"]
    
    for root, _, files in os.walk("dashboard"):
        for file in files:
            if not file.endswith(".py"):
                continue
            with open(os.path.join(root, file), "r") as f:
                content = f.read()
                
            # Remove the safety warning from the content before checking
            content_cleaned = content.replace("Paper trading only — all execution shown is simulated. No real funds, wallets, private keys, signing credentials, or real-money orders are used.", "")
            
            for term in forbidden_terms:
                assert term.lower() not in content_cleaned.lower(), f"Forbidden term {term} found in {file}"

def test_dashboard_pages_import_without_syntax_errors():
    import dashboard.pages.overview
    import dashboard.pages.predictions
    import dashboard.pages.risk_dashboard
    import dashboard.pages.paper_trades
    import dashboard.pages.agent_logs
    assert True
