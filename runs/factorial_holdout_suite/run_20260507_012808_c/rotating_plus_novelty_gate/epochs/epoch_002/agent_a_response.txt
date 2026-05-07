def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))

    def safe_moves_to(tx, ty):
        candidates = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny) and (nx, ny) not in obs_set:
                    candidates.append((dist(nx, ny, tx, ty), dx, dy))
        if not candidates:
            return [0, 0]
        candidates.sort(key=lambda t: (t[0], t[1], t[2]))
        return [candidates[0][1], candidates[0][2]]

    # If stuck on an obstacle (shouldn't), step to a safe cell deterministically
    if (sx, sy) in obs_set:
        for dx in (1, 0, -1):
            for dy in (0, 1, -1):
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny) and (nx, ny) not in obs_set:
                    return [dx, dy]
        return [0, 0]

    # Targeting: pick resource maximizing advantage (opp_time - self_time), discourage near obstacles
    best = None
    best_score = -10**18
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        if sd == 0:
            advantage = 999999
        else:
            advantage = od - sd
        # obstacle proximity penalty
        near = 0
        for ax in (rx - 1, rx, rx + 1):
            for ay in (ry - 1, ry, ry + 1):
                if (ax, ay) in obs_set:
                    near += 1
        score = advantage * 100 - near * 10 - sd
        if score > best_score:
            best_score = score
            best = (rx, ry, sd, od)

    # If no advantageous target, move to an "interference" point: reduce likelihood opponent wins next
    if best is None or best[2] >= best[3]:
        mx = (sx + ox) // 2
        my = (sy + oy) // 2
        # bias toward center for tie-breaking
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx = cx if abs(cx - mx) <= abs(cy - my) else mx
        ty = cy if abs(cx - mx) > abs(cy - my) else my
        tx = max(0, min(w - 1, tx))
        ty = max(0, min(h - 1, ty))
        return safe_moves_to(tx, ty)

    rx, ry, _, _ = best
    return safe_moves_to(rx, ry)