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

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("chase" in role)

    def dist_to_op(x, y):
        return abs(x - ox) + abs(y - oy)

    def nearest_obst_dist(x, y):
        if not obs_set:
            return 99
        md = 99
        for bx, by in obs_set:
            d = abs(x - bx) + abs(y - by)
            if d < md:
                md = d
        return md

    best = None
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            val = -10**9 if is_pursuer else 10**9
        else:
            d = dist_to_op(nx, ny)
            nd = nearest_obst_dist(nx, ny)
            # If pursuer: minimize distance; if evader: maximize distance.
            # Penalize being adjacent to obstacles; slight preference for moving.
            move_cost = (dx != 0 or dy != 0)
            if is_pursuer:
                val = (-d) + 0.35 * nd + 0.05 * move_cost
            else:
                val = (d) + 0.35 * nd + 0.05 * move_cost
        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]

    return best