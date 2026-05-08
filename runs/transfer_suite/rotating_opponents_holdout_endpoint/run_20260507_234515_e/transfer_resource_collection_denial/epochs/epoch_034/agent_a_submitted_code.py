def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((r[0], r[1]))
    if res:
        best = None
        best_score = -10**18
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            for rx, ry in res:
                ds = abs(nx - rx) + abs(ny - ry)
                do = abs(ox - rx) + abs(oy - ry)
                score = (do - ds) * 1000 - ds
                key = (score, -ds, -do, dx, dy)
                if key > best:
                    best = key
                    best_move = (dx, dy)
        return [best_move[0], best_move[1]]
    else:
        best = None
        best_move = (0, 0)
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            ds = abs(nx - ox) + abs(ny - oy)
            key = (ds, -abs(dx) - abs(dy), dx, dy)
            if best is None or key > best:
                best = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]