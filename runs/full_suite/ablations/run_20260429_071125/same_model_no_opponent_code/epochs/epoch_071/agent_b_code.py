def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort()

    if not resources:
        # fallback: drift toward center while staying safe and mildly away from opponent
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = -dist(nx, ny, cx, cy) + 0.1 * dist(nx, ny, ox, oy)
            key = (val, -nx, -ny, dx, dy)
            if best is None or key > best[0]:
                best = (key, (dx, dy))
        return best[1] if best is not None else [0, 0]

    best_overall = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # choose the resource that maximizes (opponent_distance - our_distance) after the move
        best_margin = None
        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            margin = do - ds  # positive: we are closer
            # tie-break: prefer smaller ds, then lexicographically (rx,ry)
            key_local = (margin, -ds, -rx, -ry)
            if best_margin is None or key_local > best_margin[0]:
                best_margin = (key_local, margin, ds)
        margin, ds = best_margin[1], best_margin[2]
        # slight preference to keep space from opponent when margins are similar
        val = margin * 10 - ds * 0.1 + 0.05 * dist(nx, ny, ox, oy)
        key = (val, margin, -ds, -nx, -ny, dx, dy)
        if best_overall is None or key > best_overall[0]:
            best_overall = (key, (dx, dy))

    return best_overall[1] if best_overall is not None else [0, 0]