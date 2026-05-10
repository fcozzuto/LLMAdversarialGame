def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            if x is None or y is None:
                continue
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            continue

    role = (observation.get("self_role") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "escape", "evasion"))
    is_pursuer = any(k in role for k in ("pursuer", "chaser", "catcher"))
    if not is_evader and not is_pursuer:
        is_evader = False
        is_pursuer = True

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(x, y, u, v):
        dx, dy = x - u, y - v
        return dx * dx + dy * dy

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    if is_pursuer:
        best = None
        for dx, dy, nx, ny in candidates:
            score = d2(nx, ny, ox, oy)
            # Tie-break: advance toward the evader's corner region (more likely to corner)
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            corner_dist = min(d2(nx, ny, cx, cy) for cx, cy in corners)
            key = (score, corner_dist)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    # Evader policy: head to the farthest corner from pursuer; otherwise maximize distance from pursuer.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target = max(corners, key=lambda c: d2(c[0], c[1], ox, oy))

    best = None
    for dx, dy, nx, ny in candidates:
        dist_opp = d2(nx, ny, ox, oy)
        # Prefer positions closer to target corner but only if they don't reduce distance too much.
        dist_to_target = d2(nx, ny, target[0], target[1])
        # Main objective: maximize distance from pursuer; secondary: approach target corner.
        # Small penalty for moving away from target to avoid jitter.
        key = (-dist_opp, dist_to_target)
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    return [best[1][0], best[1][1]]