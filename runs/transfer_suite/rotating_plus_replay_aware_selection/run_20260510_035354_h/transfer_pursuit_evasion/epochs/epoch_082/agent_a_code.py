def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def mdist(x, y):
        if not obstacles:
            return 4
        best = 10**9
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        return best

    best = None
    best_val = -10**18 if evader else 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dist_op = abs(nx - ox) + abs(ny - oy)
        val = dist_op
        if evader:
            val = val * 100
        else:
            val = -val * 100
        val += mdist(nx, ny) * (1 if evader else -1)
        # slight deterministic tie-break favoring staying near center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        val += center_bias * (0.01 if evader else -0.01)

        if best is None or (val > best_val if evader else val < best_val):
            best_val = val
            best = [dx, dy]

    if best is None:
        # if all moves blocked, try staying unless blocked/out of bounds (assume in bounds unless given badly)
        if (sx, sy) not in obstacles:
            return [0, 0]
        # deterministic fallback: first valid in-bounds non-obstacle
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return best