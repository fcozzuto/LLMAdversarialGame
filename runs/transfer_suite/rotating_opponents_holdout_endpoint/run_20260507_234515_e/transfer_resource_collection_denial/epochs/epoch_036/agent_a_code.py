def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    resources = observation.get("resources") or []
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if (sx + dx, sy + dy) in obs:
            return [0, 0]
        return [dx, dy]

    best = None
    best_move = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Maximize advantage to resource: larger (opponent_dist - my_dist) is better
        score = -10**9
        for rx, ry in resources:
            if (nx, ny) == (rx, ry):
                s = 10**6
            else:
                myd = abs(nx - rx) + abs(ny - ry)
                opd = abs(ox - rx) + abs(oy - ry)
                s = (opd - myd) * 20 - myd
            if s > score:
                score = s
        key = (score, -abs(dx) - abs(dy), dx, dy)  # deterministic tie-break
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]