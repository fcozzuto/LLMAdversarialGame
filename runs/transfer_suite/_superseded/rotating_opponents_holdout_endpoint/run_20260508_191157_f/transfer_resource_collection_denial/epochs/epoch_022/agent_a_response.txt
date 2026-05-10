def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    tr = int(observation.get("turns_remaining", 0))
    # Target score: strongly prefer resources we can reach no later than opponent, then by lead margin.
    best_target = None
    best_ts = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        # If we can likely secure it first, prioritize; otherwise still allow if close.
        lead = opd - myd
        secure_bonus = 12 if myd <= opd else 0
        time_bonus = 4 if myd <= tr else 0
        # Discourage chasing far-away items when behind.
        far_pen = 0.3 * myd if myd > opd else 0
        ts = secure_bonus + time_bonus + lead - far_pen
        # Tie-break deterministically: closer to bottom-right.
        ts2 = (ts, -myd, -(rx + 31 * ry))
        if best_ts is None or ts2 > best_ts:
            best_ts = ts2
            best_target = (rx, ry)

    tx, ty = best_target if best_target is not None else (sx, sy)

    # Evaluate each move by how much it improves our lead toward the chosen target, while not allowing opponent to steal "soon".
    best = None
    best_val = None
    for dx, dy, nx, ny in candidates:
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        myd0 = man(sx, sy, tx, ty)
        # Big preference for reducing distance; also keep relative advantage high.
        imp = myd0 - myd
        rel = (opd - myd)
        # If the opponent is already at/within reach of another resource we are currently worse at, slightly deter.
        steal_risk = 0
        for rx, ry in resources:
            md = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            if md > od and od <= min(tr, od):  # simple, deterministic risk proxy
                steal_risk = max(steal_risk, od - md)
        # Reward direct landing on a resource square.
        collect = 1 if (nx, ny) in map(tuple, resources) else 0
        val = (collect * 100) + (imp * 8) + (rel * 3) - (steal_risk * 2)
        # Final tie-break: prefer moves that go "down-right" (deterministic).
        val2 = (val, dx + dy, dx, dy)
        if best_val is None or val2 > best_val:
            best_val = val2
            best = [dx, dy]

    return best if best is not None else [0, 0]