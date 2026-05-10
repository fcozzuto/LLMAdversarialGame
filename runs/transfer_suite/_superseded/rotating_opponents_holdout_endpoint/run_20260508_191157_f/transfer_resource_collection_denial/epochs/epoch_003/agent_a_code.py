def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    gw, gh = observation.get("grid_width", 8), observation.get("grid_height", 8)

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def neighbors(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if dx == 0 and dy == 0:
                    continue
                if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                    yield dx, dy, nx, ny

    if not resources:
        # deterministic fallback: drift toward center while staying away from obstacles
        cx, cy = gw // 2, gh // 2
        cand = [(abs(cx - sx) + abs(cy - sy), 0, 0)]
        for dx, dy, nx, ny in neighbors(sx, sy):
            cand.append((abs(cx - nx) + abs(cy - ny), dx, dy))
        cand.sort()
        _, dx, dy = cand[0]
        return [dx, dy]

    # Prefer resources the opponent is less likely to reach first.
    best = None
    for rx, ry in resources:
        myd = abs(rx - sx) + abs(ry - sy)
        opd = abs(rx - ox) + abs(ry - oy)
        # Primary: maximize advantage (opponent farther than us)
        # Secondary: minimal my distance; Tertiary: stable order by coordinates
        adv = opd - myd
        key = (adv, -myd, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    (rx, ry) = best[1]

    # Choose a move that reduces distance to target, avoiding obstacles.
    curd = abs(rx - sx) + abs(ry - sy)
    candidates = []
    # Allow staying still as last resort.
    candidates.append((curd, 0, 0, sx, sy))
    for dx, dy, nx, ny in neighbors(sx, sy):
        d = abs(rx - nx) + abs(ry - ny)
        # Slight preference to block opponent when equally good
        od = abs(rx - ox) + abs(ry - oy)
        candidates.append((d, dx, dy, nx, ny))
    candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    _, dx, dy, _, _ = candidates[0]
    return [dx, dy]