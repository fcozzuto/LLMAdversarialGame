def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("evad" not in self_role and "evad" in opp_role)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [[-1, -1], [0, -1], [1, -1],
              [-1, 0], [0, 0], [1, 0],
              [-1, 1], [0, 1], [1, 1]]

    # deterministic tie-break: alternate preference order by turn parity
    tpar = int(observation.get("turn_index", 0)) & 1
    if tpar:
        deltas = list(reversed(deltas))

    def obstacle_clearance(x, y):
        # bonus for being farther from obstacles (including adjacent)
        if not obs:
            return 3
        md = 10
        for (ax, ay) in obs:
            d = abs(x - ax) + abs(y - ay)
            if d < md:
                md = d
        return md

    # dead-end penalty: count free neighbor cells
    def free_neighbors(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                c += 1
        return c

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = man(nx, ny, ox, oy)
        obst = obstacle_clearance(nx, ny)
        fn = free_neighbors(nx, ny)

        if pursuer:
            # chase, but also avoid being trapped; slight preference to keep distance from obstacles
            score = (-d * 10.0) + (obst * 0.8) + (fn * 0.5)
        else:
            # evade: maximize distance, keep room to move, and avoid obstacles
            score = (d * 10.0) + (fn * 0.6) + (obst * 0.8)

        # deterministic strict ordering
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]