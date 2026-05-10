def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("chase" in role)

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def min_obs_dist(x, y):
        if not obs:
            return 99
        md = 999
        for bx, by in obs:
            d = abs(x - bx) + abs(y - by)
            if d < md:
                md = d
        return md

    best = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        d = man(nx, ny, ox, oy)
        od = min_obs_dist(nx, ny)
        # Higher is better for our score.
        # Pursuer: minimize distance; avoid obstacles slightly.
        # Evader: maximize distance; prefer obstacle-free space.
        val = (-d) + (0.03 * od) if is_pursuer else (d + (0.03 * od))
        if best is None or val > best:
            best = val
            best_move = [dx, dy]

    return best_move