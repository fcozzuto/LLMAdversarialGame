def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def step_toward(tx, ty):
        dx = 0
        dy = 0
        if tx > x: dx = 1
        elif tx < x: dx = -1
        if ty > y: dy = 1
        elif ty < y: dy = -1
        return dx, dy

    # Choose resource with best advantage (self closer than opponent); deterministic tie-break.
    best = None  # (adv, d_self, d_opp, rx, ry)
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d_self = dist((x, y), (rx, ry))
        d_opp = dist((ox, oy), (rx, ry))
        adv = d_opp - d_self  # higher means we're closer / they farther
        key = (adv, d_self, d_opp, rx, ry)
        if best is None or key > best:
            best = key

    if best is not None:
        _, _, _, tx, ty = best
        cand = step_toward(tx, ty)

        # If direct step is blocked, try other deterministic deltas (8-neighborhood + stay).
        moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
        best_move = None
        best_score = None
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            # Prefer moves that reduce own distance to target, then increase advantage vs opponent, then deterministic.
            d_self = dist((nx, ny), (tx, ty))
            d_opp = dist((ox, oy), (tx, ty))
            score = (d_self * -1, d_opp - d_self, -(abs(dx) + abs(dy)), dx, dy)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
        if best_move is not None:
            return [int(best_move[0]), int(best_move[1])]
        return [0, 0]

    # No visible resources: move toward center while avoiding obstacles/opponent slightly.
    cx = (w - 1) // 2
    cy = (h - 1) // 2
    target = (cx, cy)
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d_center = dist((nx, ny), target)
        d_opp = dist((nx, ny), (ox, oy))
        # Prefer center, and keep some distance from opponent.
        score = (-d_center, -d_opp, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]