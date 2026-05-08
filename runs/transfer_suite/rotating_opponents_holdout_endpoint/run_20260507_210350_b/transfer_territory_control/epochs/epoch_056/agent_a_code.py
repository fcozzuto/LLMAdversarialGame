def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    opp_set = set()
    for c in observation.get("opponent_territory") or []:
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                opp_set.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def adj_to_op(tx, ty):
        for dx, dy in dirs[:8]:
            nx, ny = tx + dx, ty + dy
            if (nx, ny) in opp_set:
                return True
        return False

    def dman(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_key = None
    for c in unclaimed:
        if not c or len(c) < 2:
            continue
        tx, ty = int(c[0]), int(c[1])
        if not inb(tx, ty):
            continue
        dist = dman(sx, sy, tx, ty)
        score_bias = 2 if adj_to_op(tx, ty) else 0
        if best_key is None or (-(score_bias) + dist, -score_bias, tx, ty) < best_key:
            best_key = (-(score_bias) + dist, -score_bias, tx, ty)
            best = (tx, ty)

    if best is None:
        return [0, 0]

    tx, ty = best
    best_move = (0, 0)
    best_dist = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = dman(nx, ny, tx, ty)
        if best_dist is None or nd < best_dist or (nd == best_dist and (dx, dy) < best_move):
            best_dist = nd
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]