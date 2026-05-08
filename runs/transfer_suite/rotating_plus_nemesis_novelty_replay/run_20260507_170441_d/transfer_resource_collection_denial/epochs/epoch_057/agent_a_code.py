def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles if p is not None)

    if not resources:
        return [0, 0]

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        # Favor being earlier; if losing, pick least-worse and then closest.
        key = (my_d - op_d, my_d, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)

    _, tx, ty = best

    curd = dist8(sx, sy, tx, ty)
    best_move = [0, 0]
    best_key = (curd, 0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = dist8(nx, ny, tx, ty)
        # Primary: reduce distance to target; Secondary: move deterministically.
        key = (nd, dx, dy)
        if key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move