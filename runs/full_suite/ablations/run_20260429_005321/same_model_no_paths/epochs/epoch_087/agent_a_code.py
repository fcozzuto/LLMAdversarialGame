def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_t = None
        best_v = 10**18
        for rx, ry in resources:
            my_d = man(sx, sy, rx, ry)
            op_d = man(ox, oy, rx, ry)
            v = my_d - int(op_d * 1.05)  # prefer closer-than-opponent targets
            if v < best_v or (v == best_v and (my_d, rx, ry) < (best_v if best_t is None else 10**18, 0, 0)):
                best_v = v
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_my = man(nx, ny, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        # Increases advantage if we reduce our distance; slight pressure if opponent already close.
        score = -d_my + (0.12 * d_opp) - 0.02 * (abs(nx - ox) + abs(ny - oy))
        if nx == tx and ny == ty:
            score += 100000
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]