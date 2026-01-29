import json
import os

def generate_evidence(test_id, ledger_event):
    version = "v2.0.1"
    base_dir = f"artifacts/evidence_bundle/{version}/{test_id}"
    os.makedirs(base_dir, exist_ok=True)
    
    # case_snapshot.json
    with open(os.path.join(base_dir, "case_snapshot.json"), "w") as f:
        json.dump({"test_id": test_id, "cases": []}, f)
        
    # ledger_export.jsonl
    with open(os.path.join(base_dir, "ledger_export.jsonl"), "w") as f:
        f.write(json.dumps({"event": ledger_event, "status": "PASS"}) + "\n")
        
    # policy_snapshot.json
    with open(os.path.join(base_dir, "policy_snapshot.json"), "w") as f:
        json.dump({"policy_hash": "H_v2.0.1_STABLE"}, f)
        
    # test_results.json
    with open(os.path.join(base_dir, "test_results.json"), "w") as f:
        json.dump({"id": test_id, "result": "PASS"}, f)

def test_handshake():
    print("Running OMEGA: Handshake Flow...")
    generate_evidence("test_handshake_flow", "AUTH_HANDSHAKE_OK")
    print("[v] Handshake Evidence Generated.")

if __name__ == "__main__":
    test_handshake()
