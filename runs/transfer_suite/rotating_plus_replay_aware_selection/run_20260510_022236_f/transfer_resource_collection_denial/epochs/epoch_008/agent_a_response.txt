def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    tr = int(observation.get("turns_remaining", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    if not resources:
        return [0, 0]

    obs_set = set((x, y) for x, y in obstacles)

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)

        # If we're already too far to matter, deprioritize (but don't ignore completely).
        if myd > tr + 3 and opd > tr + 3:
            continue

        # Prefer taking resources we can reach first; otherwise contest when close.
        lead = opd - myd  # positive => we are closer
        contest_bonus = 10 if myd <= opd and (opd - myd) <= 2 else 0
        late_pen = 0
        if myd > tr:
            late_pen = (myd - tr)

        # Key: maximize lead, then contest_bonus, then smaller myd, then deterministic tie-break by coordinates
        key = (lead, contest_bonus, -myd, -(rx * 100 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        rx, ry = resources[0]
    else:
        rx, ry = best

    # Choose among 9 moves: diagonal allowed, stay allowed; avoid obstacles.
    candidates = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_mkey = None

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        is_block = (nx, ny) in obs_set

        d_before = cheb(sx, sy, rx, ry)
        d_after = cheb(nx, ny, rx, ry)
        improve = d_before - d_after  # positive is good

        # If opponent is very close to this resource, slightly prefer moves that reduce our distance more.
        my_gain = improve
        opp_dist = cheb(ox, oy, rx, ry)

        # Small obstacle repulsion: penalize stepping into obstacles; prefer detours only if needed.
        key = (
            my_gain,
            -is_block,
            -abs((d_after - myd_est_guess(sx, sy, rx, ry))) if False else 0,
            -d_after,
            -(dx * 3 + dy),
        )

        # Deterministic myd_est_guess placeholder removal: keep constant to preserve determinism.
        if best_mkey is None or key > best_mkey:
            best_mkey = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]