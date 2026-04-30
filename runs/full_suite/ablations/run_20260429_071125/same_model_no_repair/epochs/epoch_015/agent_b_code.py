def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_obst_pen(x, y):
        if (x, y) in occ:
            return 10**9
        pen = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            if (x+dx, y+dy) in occ:
                pen += 20
        for dx, dy in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            if (x+dx, y+dy) in occ:
                pen += 6
        return pen

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target resource we are relatively more likely to reach than opponent.
    best_target = None
    best_tscore = -10**18
    for rx, ry in resources:
        if (rx, ry) in occ:
            continue
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Prefer resources we can beat (smaller ds) and not those opponent will grab first.
        score = (do - ds) * 5 - ds
        # Slightly prefer nearer resources when tied on race.
        score += -dist(rx, ry, (w - 1) // 2, (h - 1) // 2) * 0.01
        if score > best_tscore:
            best_tscore = score
            best_target = (rx, ry)

    # If no resources, drift to a corner away from opponent, avoiding obstacles.
    if best_target is None:
        tx, ty = (0, 7) if (ox + oy) < (w - 1 + h - 1) else (7, 0)
    else:
        tx, ty = best_target

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        # Race to target; also reduce chance of opponent contesting by not stepping toward their target.
        ds_new = dist(nx, ny, tx, ty)
        do_now = dist(ox, oy, tx, ty)
        # Prefer moves that increase the gap relative to opponent.
        race = (do_now - ds_new) * 6 - ds_new
        # Avoid moving closer to opponent too aggressively (keeps paths clean).
        opp = -dist(nx, ny, ox, oy) * 0.3
        # Obstacle safety.
        safe = -adj_obst_pen(nx, ny)
        # If resources are present, bias toward any resource slightly more than pure target (prevents deadlocks).
        bias = 0.0
        if resources:
            m = 10**18
            for rx, ry in resources:
                if (rx, ry) in occ:
                    continue
                m = min(m, dist(nx, ny, rx, ry))
            bias = -m * 0.6
        val = race + opp + safe + bias
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]