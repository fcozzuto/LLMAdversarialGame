def choose_move(observation):
    turn = observation.get("turn_index", 0)
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Evaluate possible moves (dx,dy) in [-1,0,1]
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_score = -10**9

    def manh(a,b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Determine closest resource
    closest_res = None
    best_d = 10**9
    for r in resources:
        d = manh(me, r)
        if d < best_d:
            best_d = d
            closest_res = r

    # Target: if resources remain, go toward closest resource; else chase opponent
    if closest_res is not None:
        target = closest_res
    else:
        target = opp

    for dx, dy in moves:
        nx, ny = me[0] + dx, me[1] + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # simple scoring: move toward target, then prefer not moving away from opponent
        nd = [nx, ny]
        d_to_target = manh(nd, target)
        d_to_opp = manh(nd, opp)

        # Prefer reducing distance to target; breaking ties by increasing distance from opponent (to avoid easy capture)
        score = -d_to_target * 2 + (-d_to_opp)
        # Prefer staying if blocked
        if dx == 0 and dy == 0:
            score += 1

        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        # fallback: stay
        return [0, 0]
    return best