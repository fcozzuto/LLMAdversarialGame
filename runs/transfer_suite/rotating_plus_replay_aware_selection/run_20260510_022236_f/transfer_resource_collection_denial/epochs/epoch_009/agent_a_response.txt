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

        if myd > tr + 3 and opd > tr + 3:
            continue

        lead = opd - myd  # positive => we are closer
        contest_bonus = 12 if myd <= opd and (opd - myd) <= 2 else 0
        late_pen = myd - tr if myd > tr else 0

        key = (lead, contest_bonus, -myd, -(rx * 100 + ry), -late_pen)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        best = resources[0]
    tx, ty = best

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    # Candidate moves ordered deterministically
    candidates = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            candidates.append((dx, dy))
    candidates.sort(key=lambda p: (abs(p[0]) + abs(p[1]), p[0], p[1]))

    # Prefer moving toward the target (if not blocked)
    preferred = (0, 0)
    preferred = (0 if tx == sx else (1 if tx > sx else -1), 0 if ty == sy else (1 if ty > sy else -1))
    # Ensure preferred is first among candidates if present
    if preferred in candidates:
        candidates.remove(preferred)
        candidates.insert(0, preferred)

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        # Choose move that maximizes our progress vs opponent
        myd2 = cheb(nx, ny, tx, ty)
        # Opponent assumed moving greedily; use current distance only (deterministic)
        # But incorporate contesting advantage by preferring smaller myd2.
        myd_now = cheb(sx, sy, tx, ty)
        if dx == 0 and dy == 0 and (myd2 > myd_now):
            continue
        return [dx, dy]

    return [0, 0]