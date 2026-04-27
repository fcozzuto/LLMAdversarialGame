def choose_move(observation):
    turn = observation.get("turn_index", 0)
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def dist_cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    def score_for(nx, ny):
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            return -10**6
        sc = 0
        # prioritize getting closer to nearest resource than opponent
        for rx, ry in resources:
            d_my = dist((nx, ny), (rx, ry))
            d_opp = dist(opp, (rx, ry))
            sc += (d_opp - d_my)
        # slight bias to approach opponent when no resources nearby
        if not resources:
            sc += -dist((nx, ny), opp)
        return sc

    best = [0, 0]
    best_score = -10**9

    # deterministic ordering: rotate moves by turn for variety but deterministic
    idx = turn % len(moves)
    order = moves[idx:] + moves[:idx]

    for dx, dy in order:
        nx, ny = me[0] + dx, me[1] + dy
        s = score_for(nx, ny)
        if s > best_score:
            best_score = s
            best = [dx, dy]

    return best