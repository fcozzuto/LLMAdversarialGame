def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()
    is_evader = "evader" in role and "pursuer" not in role

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        c = 0
        for dxx, dyy in ((-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)):
            nx, ny = x + dxx, y + dyy
            if inside(nx, ny) and (nx, ny) not in blocked:
                c += 1
        return c

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    best_score = None

    # Deterministic preference: tie-break by (distance, -mobility, dx, dy) depending on role
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            nx, ny = sx, sy
        dist = cheb(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        if is_evader:
            # Maximize distance; avoid low-mobility traps; slight preference away from center toward far corner direction
            center_bias_x = nx - (w - 1) / 2.0
            center_bias_y = ny - (h - 1) / 2.0
            corner_dir = 1 if (center_bias_x * (ox - nx) + center_bias_y * (oy - ny)) < 0 else -1
            score = (dist, mob, corner_dir)
            key = (dist, mob, corner_dir, -dx, -dy)
            better = best_score is None or key > best_score
        else:
            # Pursuer: minimize distance; keep mobility high to avoid being squeezed by wall runner
            score = (-dist, mob)
            key = (-dist, mob, dx, dy)
            better = best_score is None or key > best_score

        if better:
            best_score = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]