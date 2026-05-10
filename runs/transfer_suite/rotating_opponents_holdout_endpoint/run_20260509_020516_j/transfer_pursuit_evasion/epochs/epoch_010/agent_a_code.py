def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Prefer closing distance; if multiple, prefer moves with more future mobility; break ties deterministically.
    best = (10**18, -10**9, 10**9, 0, 0)
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Mobility at next step (avoid stepping into dead-ends).
        mob = 0
        for ddx, ddy in deltas:
            tx, ty = nx + ddx, ny + ddy
            if valid(tx, ty):
                mob += 1

        # Opponent may be trying to evade; use asymmetric heuristic: minimize distance, maximize mob.
        dist = d2(nx, ny, ox, oy)
        # Secondary: prefer not to worsen distance if currently behind corner-to-corner motion
        self_to_opp = d2(sx, sy, ox, oy)
        dist_delta = dist - self_to_opp

        # Deterministic tie-breaker: smallest dx, then dy (by ordering via tuple below)
        cand = (dist, -mob, abs(dist_delta), dx, dy)
        if cand < best:
            best = cand
            best_move = [dx, dy]

    return best_move