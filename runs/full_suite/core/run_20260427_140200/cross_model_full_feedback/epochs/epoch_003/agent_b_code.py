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

    def manh(a,b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # choose a target: closest resource if any, else move toward opponent
    target = None
    best_d = 10**9
    for r in resources:
        d = manh(me, r)
        if d < best_d:
            best_d = d
            target = r
    if target is None:
        target = opp

    # score moves by distance to target, avoid obstacles, prefer not staying if can improve
    best_move = [0, 0]
    best_score = -10**9
    tx, ty = target

    for dx, dy in moves:
        nx, ny = me[0] + dx, me[1] + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        ndist = manh([nx, ny], target)
        # Prefer moves that reduce distance to target; tie-break by being closer to opponent
        odist = manh([nx, ny], opp)
        score = -ndist * 2 + (odist * 0)  # primary: closer to target

        # slight bias: avoid moving into cornered stalemate by staying if blocked
        if dx == 0 and dy == 0:
            score += 0  # neutral

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move