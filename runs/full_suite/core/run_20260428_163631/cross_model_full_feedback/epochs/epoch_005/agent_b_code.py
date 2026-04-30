def choose_move(observation):
    turn_index = observation.get("turn_index", 0)
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1), (0,-1), (1,-1),
              (-1, 0), (0,0), (1,0),
              (-1,1), (0,1), (1,1)]

    # valid moves excluding obstacles, but allow staying
    valid_moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            valid_moves.append((dx, dy))
    if not valid_moves:
        return [0, 0]

    # Choose a deterministic target: prioritize closest resource, then center
    resources = [tuple(r) for r in observation.get("resources", [])]
    target = None

    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    if resources:
        # pick resource that maximizes (opp distance - me distance), tie-break by coordinates
        best = None
        best_score = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_me = man((sx, sy), (rx, ry))
            d_opp = man((ox, oy), (rx, ry))
            score = (d_opp - d_me)
            if best_score is None or score > best_score or (score == best_score and (rx, ry) < best):
                best_score = score
                best = (rx, ry)
        target = best if best is not None else (w//2, h//2)
    else:
        target = (w//2, h//2)

    # Evaluate best move toward target with obstacle handling
    best_move = None
    best_val = None

    for dx, dy in valid_moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            continue
        # compute distances to target after move
        d_me = man((nx, ny), target)
        d_opp = man((ox, oy), target)
        # heuristic: prefer reducing distance to target and also keep some distance from opponent
        val = (-d_me) - max(0, (d_opp - 1))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        # fallback: move towards target if possible, else stay
        dx = target[0] - sx
        dy = target[1] - sy
        mvx = 0 if dx == 0 else (1 if dx > 0 else -1)
        mvy = 0 if dy == 0 else (1 if dy > 0 else -1)
        if (sx + mvx, sy + mvy) in obstacles or not in_bounds(sx+mvx, sy+mvy):
            return [0, 0]
        return [mvx, mvy]

    return [best_move[0], best_move[1]]