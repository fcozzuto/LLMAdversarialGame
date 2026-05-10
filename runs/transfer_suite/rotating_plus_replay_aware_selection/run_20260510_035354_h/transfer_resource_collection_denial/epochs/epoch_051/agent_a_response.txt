def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    seen = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obs and (x, y) not in seen:
                seen.add((x, y))
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        pickup = 1 if (nx, ny) in seen else 0  # seen is set of res coords
        # Evaluate best target after this move
        local_best = None
        for tx, ty in res:
            our_d = cheb(nx, ny, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            # Want positive (opp_d - our_d); reward earlier pickup strongly
            margin = opp_d - our_d
            cand = (margin, -our_d)
            if local_best is None or cand > local_best:
                local_best = cand
        score = (pickup, local_best[0], local_best[1])
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move