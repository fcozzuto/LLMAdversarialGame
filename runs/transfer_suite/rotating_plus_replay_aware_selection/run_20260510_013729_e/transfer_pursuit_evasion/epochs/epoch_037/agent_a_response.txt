def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_set.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("chase" in role)

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def nearest_obst_dist(x, y):
        md = 99
        if not obs_set:
            return md
        for bx, by in obs_set:
            d = abs(x - bx) + abs(y - by)
            if d < md:
                md = d
        return md

    def dist_to_opp(x, y):
        return abs(x - ox) + abs(y - oy)

    best_move = [0, 0]
    best_val = None

    if is_pursuer:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obs_set:
                continue
            d = dist_to_opp(nx, ny)
            nd = nearest_obst_dist(nx, ny)
            val = (-d) + (0.15 * nd) + (-0.01 * (abs(nx-ox)+abs(ny-oy)))  # deterministic slight tie bias
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]
        return best_move

    # Evader: head to the corner farthest from pursuer, while increasing distance locally and avoiding obstacles.
    target = corners[0]
    best_corner_d = -1
    for c in corners:
        cd = abs(c[0] - ox) + abs(c[1] - oy)
        if cd > best_corner_d:
            best_corner_d = cd
            target = c
    tx, ty = target

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        d = dist_to_opp(nx, ny)
        nd = nearest_obst_dist(nx, ny)
        dc = abs(nx - tx) + abs(ny - ty)
        val = d + (0.18 * nd) - (0.06 * dc)  # prefer farther from opponent, then nearer desired corner
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move