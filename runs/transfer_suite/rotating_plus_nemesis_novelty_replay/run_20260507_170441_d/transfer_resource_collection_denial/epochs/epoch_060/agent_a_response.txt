def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles if p is not None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    best_t = None
    best_key = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        adv = op_d - my_d  # larger => we are closer/sooner
        key = (-adv, my_d, rx, ry)  # pick maximum adv, then min my_d
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    op_d_const = dist8(ox, oy, tx, ty)

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_d = dist8(nx, ny, tx, ty)
        adv_after = op_d_const - my_d
        # Prefer moves that keep/extend advantage, then get closer to target
        score = (adv_after * 1000) - my_d
        # Deterministic tie-break: prefer moves closer to direct line, then fixed order
        tie = (abs((nx - tx) != 0) + abs((ny - ty) != 0), dx, dy)
        full = (score, -tie[0], tie[1], tie[2])
        if best_score is None or full > best_score:
            best_score = full
            best_move = [dx, dy]

    return best_move