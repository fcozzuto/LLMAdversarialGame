def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "fugitive"))
    is_pursuer = any(k in role for k in ("pursuer", "hunter", "seeker"))
    if not is_evader and not is_pursuer:
        is_pursuer = True
    obstacles = observation.get("obstacles") or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    # Deterministic tiebreak: prefer smallest dx, then smallest dy, then stay
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        md = abs(nx - ox) + abs(ny - oy)
        # obstacle proximity penalty to avoid getting stuck near walls
        prox = 0
        if obs:
            for (bx, by) in obs:
                d = abs(nx - bx) + abs(ny - by)
                if d == 0:
                    prox += 10**6
                else:
                    prox += 2 / (d + 0.5)
        if is_pursuer:
            # chase: minimize distance, heavily reward capture
            score = md
            if md == 0:
                score = -10**9
            score = score + 0.3 * prox
        else:
            # evade: maximize distance, avoid stepping near obstacles
            score = -md
            if md == 0:
                score = -10**9  # being caught is terrible
            score = score - 0.15 * prox
        cand = (score, dx, dy, 0 if (dx == 0 and dy == 0) else 1)
        if best is None or cand < best:
            best = cand

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]