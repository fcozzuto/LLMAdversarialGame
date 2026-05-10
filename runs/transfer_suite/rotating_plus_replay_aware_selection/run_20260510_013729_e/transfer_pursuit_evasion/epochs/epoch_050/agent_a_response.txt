def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("runner" in role)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h
    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    def adj_obs_pen(x, y):
        p = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs:
                p -= 2
        return p

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny): 
            continue
        if (nx, ny) in obs:
            continue

        d0 = md(sx, sy, ox, oy)
        d1 = md(nx, ny, ox, oy)
        center = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        free = 0
        for ddx, ddy in deltas:
            tx, ty = nx + ddx, ny + ddy
            if in_bounds(tx, ty) and (tx, ty) not in obs:
                free += 1

        if is_evader:
            score = (d1 - d0) * 6.0 + d1 * 1.0 + free * 0.15 + center * 0.02 + adj_obs_pen(nx, ny)
        else:
            score = (d0 - d1) * 6.0 - d1 * 1.0 + free * 0.15 + center * 0.02 + adj_obs_pen(nx, ny)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]