"""
End-to-End System Sanity & Verification Script for Job Intelligence Platform
Tests all core subsystems:
1. Health & Readiness checks
2. Fixture endpoint (/demo-jobs)
3. User registration & JWT authentication (login, refresh, me)
4. Job feed retrieval & keyword search
5. Deterministic preference matching engine
6. Bookmark saving & lifecycle application tracking
7. Admin metrics & scraper telemetry
8. Webhook ingestion

Usage:
  VERIFY_ADMIN_PASSWORD=<your-admin-password> python scripts/verify_system.py
"""
import os
import sys
import time
import httpx

BASE_URL = "http://localhost:8000"


def log_step(name: str, passed: bool, detail: str = ""):
    symbol = "✓ PASS" if passed else "✗ FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{symbol}{reset} - {name} {f'({detail})' if detail else ''}")


def main():
    print("=" * 60)
    print("  Job Intelligence Platform End-to-End Verification")
    print("=" * 60)

    client = httpx.Client(base_url=BASE_URL, timeout=15.0)

    # 1. Health check
    try:
        resp = client.get("/health")
        passed = resp.status_code == 200 and resp.json().get("status") == "ok"
        log_step("Basic Health Probe (/health)", passed, f"status={resp.status_code}")
    except Exception as e:
        log_step("Basic Health Probe (/health)", False, str(e))
        print("Backend API is not responding. Ensure the server or docker containers are running.")
        sys.exit(1)

    # 2. Demo Jobs Fixture Endpoint
    try:
        resp = client.get("/demo-jobs")
        data = resp.json()
        passed = resp.status_code == 200 and isinstance(data, list) and len(data) > 0
        log_step("Demo Jobs Fixture Endpoint (/demo-jobs)", passed, f"{len(data)} items returned")
    except Exception as e:
        log_step("Demo Jobs Fixture Endpoint (/demo-jobs)", False, str(e))

    # 3. User Authentication Flow
    test_email = f"tester_{int(time.time())}@example.com"
    # Use a randomised ephemeral password for the disposable test user
    import secrets
    test_password = secrets.token_urlsafe(20)
    access_token = ""
    
    # 3a. Registration
    try:
        reg_resp = client.post(
            "/api/v1/auth/register",
            json={"email": test_email, "password": test_password, "full_name": "Automated Tester"},
        )
        passed = reg_resp.status_code == 201
        log_step("User Registration (/auth/register)", passed, f"email={test_email}")
    except Exception as e:
        log_step("User Registration (/auth/register)", False, str(e))

    # 3b. Login
    refresh_token = ""
    try:
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": test_email, "password": test_password},
        )
        passed = login_resp.status_code == 200 and "access_token" in login_resp.json()
        if passed:
            access_token = login_resp.json()["access_token"]
            refresh_token = login_resp.json()["refresh_token"]
        log_step("User Authentication & JWT Issuance (/auth/login)", passed)
    except Exception as e:
        log_step("User Authentication & JWT Issuance (/auth/login)", False, str(e))

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # 3c. Get Current User Profile
    try:
        me_resp = client.get("/api/v1/auth/me", headers=auth_headers)
        passed = me_resp.status_code == 200 and me_resp.json().get("email") == test_email
        log_step("Token Validation & Current User (/auth/me)", passed)
    except Exception as e:
        log_step("Token Validation & Current User (/auth/me)", False, str(e))

    # 3d. Token Refresh
    try:
        ref_resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        passed = ref_resp.status_code == 200 and "access_token" in ref_resp.json()
        if passed:
            access_token = ref_resp.json()["access_token"]
            auth_headers = {"Authorization": f"Bearer {access_token}"}
        log_step("Refresh Token Rotation (/auth/refresh)", passed)
    except Exception as e:
        log_step("Refresh Token Rotation (/auth/refresh)", False, str(e))

    # 4. Job Preferences Configuration
    try:
        pref_resp = client.put(
            "/api/v1/preferences",
            headers=auth_headers,
            json={
                "keywords": ["Python", "FastAPI", "Remote", "Backend"],
                "locations": ["Remote", "Worldwide"],
                "work_modes": ["Remote"],
                "employment_types": ["Full-time"],
                "min_salary": 60000,
            },
        )
        passed = pref_resp.status_code == 200 and "Python" in pref_resp.json().get("keywords", [])
        log_step("Job Preference Configuration (/preferences)", passed)
    except Exception as e:
        log_step("Job Preference Configuration (/preferences)", False, str(e))

    # 5. Job Feed Retrieval & Match Scoring
    first_job_id = None
    try:
        jobs_resp = client.get("/api/v1/jobs?page=1&page_size=10", headers=auth_headers)
        passed = jobs_resp.status_code == 200
        items = jobs_resp.json().get("items", [])
        if passed and len(items) > 0:
            first_job_id = items[0]["id"]
            score = items[0].get("match_score")
            reasons = items[0].get("match_reasons", [])
            log_step(
                "Job Feed & Match Scoring (/jobs)",
                passed,
                f"{len(items)} jobs loaded, top match={score}%, reasons={len(reasons)}",
            )
        else:
            log_step("Job Feed & Match Scoring (/jobs)", passed, f"{len(items)} jobs found")
    except Exception as e:
        log_step("Job Feed & Match Scoring (/jobs)", False, str(e))

    # 6. Search Filtering
    try:
        search_resp = client.get("/api/v1/jobs/search?q=Python", headers=auth_headers)
        passed = search_resp.status_code == 200
        found = len(search_resp.json().get("items", []))
        log_step("Keyword Search Filter (/jobs/search?q=Python)", passed, f"{found} results")
    except Exception as e:
        log_step("Keyword Search Filter (/jobs/search?q=Python)", False, str(e))

    # 7. Job Bookmarking & Application Tracking
    if first_job_id:
        # Save Job
        try:
            save_resp = client.post(f"/api/v1/jobs/{first_job_id}/save", headers=auth_headers)
            passed = save_resp.status_code == 201
            log_step(f"Save / Bookmark Job (/jobs/{first_job_id}/save)", passed)
        except Exception as e:
            log_step(f"Save / Bookmark Job (/jobs/{first_job_id}/save)", False, str(e))

        # Retrieve Saved Jobs
        try:
            saved_resp = client.get("/api/v1/jobs/saved/me", headers=auth_headers)
            passed = saved_resp.status_code == 200 and len(saved_resp.json()) >= 1
            log_step("Get User Saved Jobs (/jobs/saved/me)", passed, f"{len(saved_resp.json())} saved")
        except Exception as e:
            log_step("Get User Saved Jobs (/jobs/saved/me)", False, str(e))

        # Create Application Track Record
        app_id = None
        try:
            app_resp = client.post(
                "/api/v1/applications",
                headers=auth_headers,
                json={
                    "job_id": first_job_id,
                    "status": "applied",
                    "notes": "Automated verification test application note.",
                },
            )
            passed = app_resp.status_code == 201
            if passed:
                app_id = app_resp.json()["id"]
            log_step("Track Job Application (/applications)", passed, f"status=applied")
        except Exception as e:
            log_step("Track Job Application (/applications)", False, str(e))

        # Update Application Status
        if app_id:
            try:
                patch_resp = client.patch(
                    f"/api/v1/applications/{app_id}",
                    headers=auth_headers,
                    json={"status": "interview", "notes": "Interview scheduled."},
                )
                passed = patch_resp.status_code == 200 and patch_resp.json().get("status") == "interview"
                log_step("Update Application Lifecycle (/applications/:id)", passed, "status -> interview")
            except Exception as e:
                log_step("Update Application Lifecycle (/applications/:id)", False, str(e))

    # 8. Webhook Ingestion Probe
    try:
        hook_resp = client.post(
            "/api/v1/webhooks/job-events",
            json={
                "event": "job.match",
                "match_score": 95,
                "job": {"id": 1, "title": "Senior Python Backend Engineer"},
                "user": {"id": 1, "email": "test@example.com"},
            },
        )
        passed = hook_resp.status_code == 200 and hook_resp.json().get("processed") is True
        log_step("Webhook Ingestion Endpoint (/webhooks/job-events)", passed)
    except Exception as e:
        log_step("Webhook Ingestion Endpoint (/webhooks/job-events)", False, str(e))

    # 9. Admin Superuser Authentication & Telemetry
    # Admin password is read from VERIFY_ADMIN_PASSWORD environment variable
    admin_password = os.environ.get("VERIFY_ADMIN_PASSWORD", "")
    if not admin_password:
        log_step("Admin Superuser Portal & Stats (/admin/stats)", False,
                 "VERIFY_ADMIN_PASSWORD env var not set — skipping admin tests")
    else:
        try:
            admin_login = client.post(
                "/api/v1/auth/login",
                json={"email": "admin@jobintel.io", "password": admin_password},
            )
            if admin_login.status_code == 200:
                admin_token = admin_login.json()["access_token"]
                admin_headers = {"Authorization": f"Bearer {admin_token}"}

                stats_resp = client.get("/api/v1/admin/stats", headers=admin_headers)
                stats = stats_resp.json()
                passed = stats_resp.status_code == 200 and "total_jobs" in stats
                log_step(
                    "Admin Superuser Portal & Stats (/admin/stats)",
                    passed,
                    f"jobs={stats.get('total_jobs')}, sources={stats.get('total_sources')}, users={stats.get('total_users')}",
                )

                src_resp = client.get("/api/v1/admin/sources", headers=admin_headers)
                passed = src_resp.status_code == 200 and len(src_resp.json()) >= 1
                log_step(
                    "Admin Job Source Management (/admin/sources)",
                    passed,
                    f"{len(src_resp.json())} sources configured",
                )
            else:
                log_step("Admin Superuser Login", False, f"status={admin_login.status_code}")
        except Exception as e:
            log_step("Admin Superuser Portal & Stats", False, str(e))

    print("=" * 60)
    print("  Verification Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
