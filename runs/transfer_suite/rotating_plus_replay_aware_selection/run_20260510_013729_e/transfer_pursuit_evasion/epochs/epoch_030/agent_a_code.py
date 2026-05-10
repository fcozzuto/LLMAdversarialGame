def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    ob = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    role = (observation.get("self_role") or "").lower()
    pursuer = role != "evader"  # default to pursuer behavior if unknown

    def dist(x, y):
        return abs(x - ox) + abs(y - oy)

    def mobility(x, y):
        m = 0
        for ddx, ddy in deltas:
            nx, ny = x + ddx, y + ddy
            if in_bounds(nx, ny) and (nx, ny) not in ob:
                m += 1
        return m

    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in ob:
            continue
        md = dist(nx, ny)
        mob = mobility(nx, ny)
        still = 1 if (dx == 0 and dy == 0) else 0
        if pursuer:
            key = (-md, -mob, still, dx, dy)  # get closer, keep options
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]
        else:
            key = (md, -mob, still, dx, dy)   # get farther, reduce trap likelihood
            if best_key is None or key > best_key:
                best_key = key
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best