def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except Exception:
        sx, sy, ox, oy = 0, 0, 0, 0

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            try:
                x, y = int(x), int(y)
            except Exception:
                continue
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            try:
                x, y = int(x), int(y)
            except Exception:
                continue
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    cx, cy = sx, sy
    target = None
    if unclaimed:
        best = None
        for x, y in unclaimed:
            d = abs(x - cx) + abs(y - cy)
            t = abs(x - (w - 1) // 2) + abs(y - (h - 1) // 2)
            # Prefer closer to us, and more central among equal distances
            score = (-d, -t)
            if best is None or score > best[0]:
                best = (score, (x, y))
        target = best[1]

    if target is None:
        target = (ox, oy)

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist_to_target = abs(nx - target[0]) + abs(ny - target[1])
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        # Prefer reducing distance to target, and staying away from opponent when possible
        val = (-dist_to_target, dist_to_opp, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If all moves are blocked, stay in place (still valid as integer dx,dy)
    return [best_move[0], best_move[1]]