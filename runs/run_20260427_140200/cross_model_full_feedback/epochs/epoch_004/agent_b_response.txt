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

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    def cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    best_move = [0, 0]
    best_score = -10**9

    # If resources exist, prioritize moving towards a resource where we have advantage over opponent
    if resources:
        for dx, dy in moves:
            nx, ny = me[0] + dx, me[1] + dy
            if not in_bounds(nx, ny): 
                continue
            if (nx, ny) in obstacles:
                continue
            # evaluate best resource for this candidate position
            score = 0
            for rx, ry in resources:
                d_my = dist((nx, ny), (rx, ry))
                d_opp = dist((opp[0], opp[1]), (rx, ry))
                # advantage if we are closer to resource than opponent
                score += (d_opp - d_my)
            # prefer being closer to opponent slightly to attempt blocking; but main is resource advantage
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move

    # No resources: head towards opponent to pressure, avoid obstacles
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = me[0] + dx, me[1] + dy
        if not in_bounds(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        # prefer moves that reduce Chebyshev distance to opponent
        od = cheb((nx, ny), (opp[0], opp[1]))
        # small tie-break: if staying, allow only if no better
        score = -od
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move