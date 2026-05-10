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

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x, y):
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

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            score = -10**12 if is_pursuer else -10**12
        else:
            d = dist(nx, ny)
            nd = nearest_obst_dist(nx, ny)
            # small deterministic tie-break towards reducing/expanding Manhattan distance first
            # plus obstacle clearance preference to reduce collisions/traps
            if is_pursuer:
                score = -d * 1000 + nd * 3
            else:
                score = d * 1000 + nd * 3
        if best_score is None or (score > best_score):
            best_score = score
            best_move = [dx, dy]

    return best_move