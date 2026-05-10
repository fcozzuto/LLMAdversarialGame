def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    xp, yp = int(sp[0]), int(sp[1])
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set("obstacles")
    myt = to_set("self_territory")
    opt = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_score(x, y):
        if (x, y) in obstacles:
            return -10**9
        if (x, y) in unclaimed:
            return 120 - (abs(x - cx) + abs(y - cy)) * 2
        if (x, y) in opt:
            return 85 - (abs(x - xp) + abs(y - yp)) * 2 - (abs(x - cx) + abs(y - cy))
        if (x, y) in myt:
            return 35 - (abs(x - cx) + abs(y - cy))
        return 10 - (abs(x - cx) + abs(y - cy))

    best = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = xp + dx, yp + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        val = cell_score(nx, ny)
        # Encourage closing distance to center when we're already strong; otherwise, prefer capture/claim.
        t = int(observation.get("turn_index") or 0)
        if t % 10 == 9:
            val += 10  # slight nudge right before leader bonus trigger
        val += (-(abs(nx - cx) + abs(ny - cy))) * 0.5
        # Deterministic tie-break: prefer moves in fixed dir order already, then lexicographic dx,dy
        if val > best_val:
            best_val = val
            best = (dx, dy)

    dx, dy = best
    if not (-1 <= dx <= 1 and -1 <= dy <= 1):
        return [0, 0]
    return [int(dx), int(dy)]