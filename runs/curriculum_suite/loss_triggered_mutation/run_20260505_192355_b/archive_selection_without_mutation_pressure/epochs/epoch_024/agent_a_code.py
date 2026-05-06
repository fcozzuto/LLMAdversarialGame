def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obs_list)
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    best_move = valid[0]
    best_key = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        best_adv_for_move = None
        best_myd_for_move = None
        for rx, ry in resources:
            myd = manh(nx, ny, rx, ry)
            opd = manh(ox, oy, rx, ry)
            adv = opd - myd
            if best_adv_for_move is None or adv > best_adv_for_move or (adv == best_adv_for_move and myd < best_myd_for_move):
                best_adv_for_move = adv
                best_myd_for_move = myd
        key = (-best_adv_for_move, best_myd_for_move, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]