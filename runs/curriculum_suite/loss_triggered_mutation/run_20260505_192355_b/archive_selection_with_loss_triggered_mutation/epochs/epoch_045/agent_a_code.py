def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    if not res:
        tx, ty = (w // 2), (h // 2)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_score = -10**18

    # Evaluate each move by contesting resources opponent would otherwise reach first.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        score = 0
        # Prefer moves that reduce (self_dist - opponent_dist) for the best contested resource.
        best_delta = 10**9
        best_opp_dist = 10**9
        for rx, ry in res:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            delta = sd - od
            if delta < best_delta or (delta == best_delta and od < best_opp_dist):
                best_delta = delta
                best_opp_dist = od
        # Higher is better: negative delta is good (we are closer).
        score = (-best_delta) * 4 - best_opp_dist * 0.25 - (abs(nx - ox) + abs(ny - oy)) * 0.02
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move