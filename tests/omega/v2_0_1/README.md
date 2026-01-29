# OMEGA v2.0.1 Test Suite (Scaffold)

## Coverage Targets
This suite validates the non-negotiable DoDs for the Trust Boundary release:

1. **Deny-by-default**: Verify that any call to a bridge tool without valid auth fails with `ERR_SCOPE_LACK`.
2. **Handshake (rotation/expiry)**: 
    - Simulate expired JWT -> Verify `ERR_ID_EXPIRED`.
    - Simulate revoked certificate -> Verify `ERR_REVOKED`.
3. **Replay protection (nonce+ttl)**: 
    - Reuse nonce within 5m -> Verify `ERR_REPLAY`.
    - Use nonce after 10m -> Verify `ERR_ID_EXPIRED` (due to TTL).
4. **Revocation enforcement**: Verify that a "kill" signal from AAA Court reaches the bridge in < 1s.
5. **Audit schema completeness**: Verify that every decision event in `RiskLedger` contains the mandatory 7 fields.
6. **Court auto-trigger**: Verify that a replay attack triggers a new Case File in `aaa-tpl-docs/internal/development/audits/`.

## Execution
Run via:
```bash
./scripts/run_omega_v2.sh --version v2.0.1
```
