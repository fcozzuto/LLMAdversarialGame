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

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        adv = op_d - my_d  # positive means we are closer/equal
        # Prefer resources we can take (adv high), then closer to us, then stable tie-break by coords
        key = (-adv, my_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    best_move = [0, 0]
    best_mkey = None
    cur_self_d = dist8(sx, sy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = dist8(nx, ny, tx, ty)
        # Maximize our improvement against opponent for this target; also avoid increasing distance too much
        self_adv = dist8(ox, oy, tx, ty) - nd
        step = max(abs(dx), abs(dy))
        move_toward = cur_self_d - nd
        # Secondary: prefer not to waste moves and avoid standing still if another valid improves
        key = (-self_adv, -move_toward, step == 0, nd, nx, ny)
        if best_mkey is None or key < best_mkey:
            best_mkey = key
            best_move = [dx, dy]

    return best_move