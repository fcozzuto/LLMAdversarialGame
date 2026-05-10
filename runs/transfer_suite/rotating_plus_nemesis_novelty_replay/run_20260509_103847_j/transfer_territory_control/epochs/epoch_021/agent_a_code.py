def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Deterministic candidate targets: prefer cells we can reach sooner than opponent and that are not adjacent to obstacles.
    candidates = []
    threshold = 6
    for tx, ty in unT:
        d1 = man(sx, sy, tx, ty)
        d2 = man(ox, oy, tx, ty)
        if d1 <= threshold and d1 <= d2:
            adj_obs = 0
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = tx + dx, ty + dy
                if (nx, ny) in obs:
                    adj_obs += 1
            candidates.append((d2 - d1, adj_obs, tx, ty))
    candidates.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
    if not candidates:
        # fallback: also consider unclaimed reachable regardless, but bias away from opponent
        all_un = list(unT)
        all_un.sort(key=lambda p: (man(sx, sy, p[0], p[1]) + 2 * man(ox, oy, p[0], p[1]), p[0], p[1]))
        candidates = [(0, 0, p[0], p[1]) for p in all_un[:12]]
    else:
        candidates = candidates[:12]

    best = (10**9, 10**9, 0, 0)
    # Evaluate each possible next move using which target we would be closest to after moving.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Immediate danger: being closer to opponent territory.
        danger = min((man(nx, ny, px, py) for px, py in opT), default=6)
        # Prefer moves that reduce distance to best reachable targets and keep distance from opponent.
        # Also allow opportunistic flipping by nudging toward opponent territory cells if no good unclaimed.
        best_target_dist = 10**9
        best_adv = -10**9
        for _, _, tx, ty in candidates:
            d_after = man(nx, ny, tx, ty)
            best_target_dist = min(best_target_dist, d_after)
            adv = (man(ox, oy, tx, ty) - d_after)
            best_adv = max(best_adv, adv)
        # Tie-break deterministically by preferring moves that reduce man to center-ish (4,4).
        center_bias = man(nx, ny, 4, 4)
        score_key = (best_target_dist, -best_adv, -danger, center_bias, dx, dy)
        if score_key < best:
            best = score_key

    return [int(best[4]), int(best[5])]