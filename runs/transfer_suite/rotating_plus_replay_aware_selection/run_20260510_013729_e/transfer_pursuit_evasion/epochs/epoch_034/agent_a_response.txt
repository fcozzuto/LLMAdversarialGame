def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    ob = []
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ob.append((int(p[0]), int(p[1])))
    obs_set = set(ob)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    role = str(observation.get("self_role") or "")
    is_evader = "evad" in role.lower()

    def man(x, y):
        return abs(x - ox) + abs(y - oy)

    def min_dist_to_obstacle(x, y):
        if not ob:
            return 99
        md = 99
        for bx, by in ob:
            d = abs(x - bx) + abs(y - by)
            if d < md:
                md = d
        return md

    def mobility(x, y):
        m = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obs_set:
                m += 1
        return m

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        d = man(nx, ny)
        md = min_dist_to_obstacle(nx, ny)
        mob = mobility(nx, ny)
        if is_evader:
            score = (d * 10.0) + (mob * 1.0) + (md * 0.2)
            if best_score is None or score > best_score:
                best_score, best_move = score, [dx, dy]
        else:
            score = (-d * 10.0) + (mob * 1.0) + (md * 0.2)
            if best_score is None or score > best_score:
                best_score, best_move = score, [dx, dy]

    return [int(best_move[0]), int(best_move[1])]