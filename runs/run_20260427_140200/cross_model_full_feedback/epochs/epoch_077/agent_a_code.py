def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(a, b, c, d):
        da = abs(a - c)
        db = abs(b - d)
        return da if da > db else db

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd or (d == bestd and (best is None or (dx, dy) < best)):
                bestd = d
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    best_move = None
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not legal(nx, ny):
            continue
        # For this hypothetical move, choose the resource where we gain most over opponent.
        # Also break ties by preferring smaller our distance to that resource and then move order.
        local_best = -10**18
        local_dme = 10**9
        local_res = None
        for rx, ry in resources:
            dme = cheb(nx, ny, rx, ry)
            dpp = cheb(ox, oy, rx, ry)
            gain = dpp - dme
            if gain > local_best or (gain == local_best and (dme < local_dme or (dme == local_dme and (local_res is None or (rx, ry) < local_res)))):
                local_best = gain
                local_dme = dme
                local_res = (rx, ry)
        if local_best > best_val or (local_best == best_val and (dx, dy) < (best_move if best_move is not None else (9, 9))):
            best_val = local_best
            best_move = (dx, dy)

    return list(best_move if best_move is not None else (0, 0))