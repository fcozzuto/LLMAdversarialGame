def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("chase" in role) or ("hunter" in role)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def nearest_obs_dist(x, y):
        if not obs:
            return 99
        d = 99
        for bx, by in obs:
            dd = abs(x - bx) + abs(y - by)
            if dd < d:
                d = dd
        return d

    target_corner = max(corners, key=lambda c: man(c[0], c[1], ox, oy)) if not is_pursuer else min(corners, key=lambda c: man(c[0], c[1], ox, oy))

    best = None
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        dpo = man(nx, ny, ox, oy)
        clear = nearest_obs_dist(nx, ny)
        corner_dist = man(nx, ny, target_corner[0], target_corner[1])
        if is_pursuer:
            score = (-dpo) + 0.08 * clear - 0.01 * corner_dist
        else:
            score = (dpo) + 0.08 * clear - 0.01 * corner_dist
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best