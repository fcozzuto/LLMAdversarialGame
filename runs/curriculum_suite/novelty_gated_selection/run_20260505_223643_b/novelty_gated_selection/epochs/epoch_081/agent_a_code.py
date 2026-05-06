def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def d(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick a race-winning target: minimize (self_dist - 1.05*opp_dist) with tie-breaks.
    best_cell = None
    best_key = None
    for rx, ry in resources:
        sd = d(sx, sy, rx, ry)
        od = d(ox, oy, rx, ry)
        key = (sd - 1.05 * od, sd, -od, (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_cell = (rx, ry)

    tx, ty = best_cell

    # Among legal moves, maximize expected improvement to target and deny opponent.
    # Utility uses next position distances; also lightly penalize moving away from target.
    best_move = [0, 0]
    best_util = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_nd = d(nx, ny, tx, ty)
        opp_d = d(ox, oy, tx, ty)

        # Prefer smaller self_nd; if close, also try to keep opponent farther.
        util = (-self_nd, opp_d, -((tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)), dx * dx + dy * dy * 0, nx, ny)
        if best_util is None or util > best_util:
            best_util = util
            best_move = [dx, dy]

    return best_move