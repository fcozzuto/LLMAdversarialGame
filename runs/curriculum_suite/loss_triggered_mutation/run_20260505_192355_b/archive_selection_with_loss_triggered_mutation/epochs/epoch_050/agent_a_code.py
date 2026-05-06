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

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    if res:
        best = None
        best_key = None
        for rx, ry in res:
            sd = dist((sx, sy), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            gap = od - sd  # positive means we are closer than opponent
            # Deterministic tie-break: prefer lower sd, then lexicographically smaller resource
            key = (gap, -sd, -((rx + ry) % 2), -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        # No visible resources: move toward nearest edge to stay competitive
        targets = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        tx, ty = min(targets, key=lambda t: dist((sx, sy), t))

    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Evaluate candidate moves
    best_move = [0, 0]
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        nd = dist((nx, ny), (tx, ty))
        od_after = dist((ox, oy), (tx, ty))
        # Prefer: reach target (lower nd), improve relative advantage, and match desired direction
        score = (-nd, (od_after - nd), -(0 if (dx == desired_dx and dy == desired_dy) else 1), -abs(dx) - abs(dy))
        if best_score == -10**9 or score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If all moves blocked, stay (engine will keep in place)
    if best_move is None:
        return [0, 0]
    return best_move