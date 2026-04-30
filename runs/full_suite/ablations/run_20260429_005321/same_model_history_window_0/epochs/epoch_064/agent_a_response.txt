def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def clamp(a, lo, hi):
        return lo if a < lo else hi if a > hi else a

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    res_set = set(tuple(p) for p in resources)

    if resources:
        best = None
        for rx, ry in resources:
            d1 = max(abs(rx - sx), abs(ry - sy))
            d2 = max(abs(rx - ox), abs(ry - oy))
            # Prefer resources we can reach sooner; if close, prefer ones that deny opponent.
            score = (d2 - d1, -d1, -(rx + ry), -abs((rx - w/2)) - abs((ry - h/2)))
            if best is None or score > best[0]:
                best = (score, (rx, ry))
        tx, ty = best[1]
    else:
        # If no resources, drift to center deterministically
        tx, ty = (w - 1) // 2, (h - 1) // 2

    cx, cy = sx, sy
    # If already on a resource, step toward a "runner-up" to avoid dithering
    if (cx, cy) in res_set and resources:
        # choose second best by shifting tie-break deterministically
        resources2 = [p for p in resources if tuple(p) != (cx, cy)]
        if resources2:
            best2 = None
            for rx, ry in resources2:
                d1 = max(abs(rx - cx), abs(ry - cy))
                d2 = max(abs(rx - ox), abs(ry - oy))
                score = (d2 - d1, -d1, (rx * 3 + ry * 5) % 7, -(rx + ry))
                if best2 is None or score > best2[0]:
                    best2 = (score, (rx, ry))
            tx, ty = best2[1]

    # Obstacle-aware greedy step: among moves that keep you in bounds and not into obstacles,
    # pick move that minimizes self distance to target and then maximizes distance from opponent.
    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = cx + dx, cy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_t = max(abs(tx - nx), abs(ty - ny))
        d_opp = max(abs(ox - nx), abs(oy - ny))
        # If opponent is very close to target, prefer moves that increase their distance.
        opp_to_t = max(abs(tx - ox), abs(ty - oy))
        key = (-(d_to_t), d_opp, -opp_to_t, (dx, dy))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]