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
        "dashboard/charts.py"
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

def test_all_pages_call_safety_banner():
    pages = [
        "dashboard/pages/overview.py",
        "dashboard/pages/predictions.py",
        "dashboard/pages/risk_dashboard.py",
        "dashboard/pages/paper_trades.py",
        "dashboard/pages/agent_logs.py",
    ]
    for page in pages:
        with open(page, "r") as f:
            content = f.read()
            assert "render_safety_banner()" in content, f"{page} is missing render_safety_banner()"

def test_no_forbidden_terms_except_safety_warning():
    forbidden_terms = ["Place Trade", "Execute Trade", "Connect Wallet", "Private Key", "Funded Account"]
    
    for root, _, files in os.walk("dashboard"):
        for file in files:
            if not file.endswith(".py"):
                continue
            with open(os.path.join(root, file), "r") as f:
                content = f.read()
                
            content_cleaned = content.replace("Paper trading only — all execution shown is simulated. No real funds, wallets, private keys, signing credentials, or real-money orders are used.", "")
            
            for term in forbidden_terms:
                assert term.lower() not in content_cleaned.lower(), f"Forbidden term '{term}' found in {file}"

def test_dashboard_uses_current_streamlit_width_api():
    dashboard_source = ""
    for root, _, files in os.walk("dashboard"):
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), "r") as f:
                    dashboard_source += f.read()

    assert "use_container_width" not in dashboard_source
    assert 'width="stretch"' in dashboard_source

def test_required_page_headings_exist():
    required_headings = [
        "Market Watch",
        "Edge Matrix",
        "Probability Tracker",
        "Risk-Gated Decisions",
        "Paper Orders",
        "Simulated Positions",
        "Agent Step Logs"
    ]
    all_content = ""
    for root, _, files in os.walk("dashboard"):
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), "r") as f:
                    all_content += f.read()
                    
    for heading in required_headings:
        assert heading in all_content, f"Required heading '{heading}' missing from dashboard files"

def test_watch_text_displayed_as_observation():
    with open("dashboard/components.py", "r") as f:
        comp_content = f.read()
    with open("dashboard/pages/risk_dashboard.py", "r") as f:
        risk_content = f.read()
        
    assert "Observation Only" in comp_content or "Observation only" in comp_content or "Observation only" in risk_content

def test_dashboard_pages_import_without_syntax_errors():
    import dashboard.pages.overview
    import dashboard.pages.predictions
    import dashboard.pages.risk_dashboard
    import dashboard.pages.paper_trades
    import dashboard.pages.agent_logs
    assert True
