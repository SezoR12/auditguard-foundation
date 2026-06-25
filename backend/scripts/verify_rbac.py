import sys
import json
import urllib.request
import urllib.error

def verify_rbac():
    print("=================================================================")
    print("       AuditCore Automated RBAC & Arabic 403 Verification       ")
    print("=================================================================")
    
    base_url = "http://localhost:8000"
    
    # 1. Login as auditor
    login_url = f"{base_url}/auth/login-json"
    login_data = json.dumps({"email": "auditor@auditcore.local", "password": "Auditor123!"}).encode("utf-8")
    req = urllib.request.Request(login_url, data=login_data, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode("utf-8"))
            access_token = data.get("access_token")
            print("[1/3] Successfully logged in as auditor@auditcore.local and received JWT access token.")
    except Exception as e:
        print(f"[error] Failed to login as auditor: {e}")
        sys.exit(1)

    # 2. Attempt to access /owner/ping as auditor
    owner_url = f"{base_url}/owner/ping"
    req_owner = urllib.request.Request(owner_url, headers={"Authorization": f"Bearer {access_token}"})
    
    try:
        with urllib.request.urlopen(req_owner) as res:
            print("[error] Auditor successfully accessed /owner/ping! RBAC failed.")
            sys.exit(1)
    except urllib.error.HTTPError as err:
        status = err.code
        body = err.read().decode("utf-8")
        print(f"[2/3] Auditor calling /owner/ping received HTTP status: {status}")
        print(f"[3/3] Response body: {body}")
        
        expected_msg = "ليس لديك صلاحية الوصول إلى هذا المورد"
        if status == 403 and expected_msg in body:
            print("\n[SUCCESS] Automated check passed: Auditor correctly received 403 with required Arabic detail.")
        else:
            print(f"\n[FAILURE] Expected status 403 and Arabic message '{expected_msg}', but got status {status} and body: {body}")
            sys.exit(1)
    except Exception as e:
        print(f"[error] Unexpected error during RBAC verification: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_rbac()
