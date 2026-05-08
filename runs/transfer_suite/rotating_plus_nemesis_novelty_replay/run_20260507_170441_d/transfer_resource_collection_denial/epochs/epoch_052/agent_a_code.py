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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        adv = my_d - op_d  # smaller => we are closer
        # prefer winning race to the resource; tie-break by our distance then coords
        key = (adv, my_d, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry), adv, my_d, op_d)
    (k, (tx, ty), adv, my_d, op_d) = best

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            self_d = dist8(nx, ny, tx, ty)
            opp_d = dist8(ox, oy, tx, ty)
            # prefer decreasing our distance, and if race is close, prefer states where we are not behind
            race_gap = self_d - opp_d
            valid.append((race_gap, self_d, nx, ny))
    if not valid:
        return [0, 0]

    valid.sort()
    _, _, nx, ny = valid[0]
    return [nx - sx, ny - sy]