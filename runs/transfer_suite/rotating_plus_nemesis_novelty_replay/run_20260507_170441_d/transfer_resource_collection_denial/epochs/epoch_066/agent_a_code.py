def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((p[0], p[1]))

    if not resources:
        return [0, 0]

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    best_cell = None
    best_key = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        adv = op_d - my_d
        key = (-adv, my_d, rx, ry)  # higher adv first; then closer
        if best_key is None or key < best_key:
            best_key = key
            best_cell = (rx, ry)

    tx, ty = best_cell
    cur_d = dist8(sx, sy, tx, ty)

    best_move = [0, 0]
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = dist8(nx, ny, tx, ty)
        self_adv = dist8(ox, oy, tx, ty) - nd
        # Prefer moves that improve time to target (smaller nd), and avoid stalls, deterministically
        mkey = (-self_adv, nd, 0 if (dx, dy) == (0, 0) else 1, dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = [dx, dy]

    if best_mkey is None:
        return [0, 0]
    return best_move