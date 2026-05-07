def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        rx, ry = int(r[0]), int(r[1])
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
            resources.append((rx, ry))

    if not resources:
        return [0, 0]

    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    def dist_cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    scored = []
    for rx, ry in resources:
        self_d = dist_cheb((sx, sy), (rx, ry))
        opp_d = dist_cheb((ox, oy), (rx, ry))
        steal = opp_d - self_d  # prefer where opponent is farther
        side_bias = (rx + ry) - (sx + sy)
        scored.append((steal, -self_d, side_bias, rx, ry))
    scored.sort(reverse=True)
    _, _, _, tx, ty = scored[0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        cur_d = dist_cheb((sx, sy), (tx, ty))
        new_d = dist_cheb((nx, ny), (tx, ty))
        # primary: decrease distance; secondary: make ourselves earlier than opponent (if possible)
        self_margin = dist_cheb((ox, oy), (tx, ty)) - new_d
        key = (-(new_d), -(self_margin), abs(tx - nx) + abs(ty - ny), dx, dy, cur_d - new_d)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    if best_key is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]