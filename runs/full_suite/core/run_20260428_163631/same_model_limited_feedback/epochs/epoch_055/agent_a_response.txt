def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        # Drift toward opponent's side deterministically
        dx = 1 if sx < w - 1 else (-1 if sx > 0 else 0)
        dy = 1 if sy < h - 1 else (-1 if sy > 0 else 0)
        return [max(-1, min(1, dx)), max(-1, min(1, dy))]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        d = abs(ax - bx) + abs(ay - by)
        d2 = (ax - bx) * (ax - bx) + (ay - by) * (ay - by)
        return d, d2

    # Choose best target resource: prioritize being much closer than opponent
    best = None
    bs = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd1, sd2 = dist((sx, sy), (rx, ry))
        od1, od2 = dist((ox, oy), (rx, ry))
        # Higher is better: being closer and also not too far in absolute terms
        score = (od1 - sd1) * 100 - sd1 * 3 - sd2 * 0.001
        # Tie-break: deterministic preference by coordinates
        score += (7 - rx) * 0.0001 + (7 - ry) * 0.00001
        if bs is None or score > bs:
            bs = score
            best = (rx, ry)
    tx, ty = best

    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # If we land on a resource, prioritize it heavily
        val = 0.0
        if (nx, ny) in resources:
            val += 1e6
        # Prefer reducing distance to target
        nd1, nd2 = dist((nx, ny), (tx, ty))
        sd1, _ = dist((sx, sy), (tx, ty))
        val += (sd1 - nd1) * 50 - nd1 * 5 - nd2 * 0.001
        # Also consider opponent distance pressure at next step toward same target
        nod1, _ = dist((ox, oy), (tx, ty))
        val += (nod1 - nd1) * 8
        # Deterministic tie-break: prefer smaller dx, then smaller dy
        val += (1 - (dx + 1)) * 1e-6 + (1 - (dy + 1)) * 1e-9
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]