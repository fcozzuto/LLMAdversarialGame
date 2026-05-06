def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))
    resources = observation.get("resources", []) or []
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    tx = w // 2
    ty = h // 2
    if resources:
        best = None
        for r in resources:
            if r and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
                if valid(rx, ry):
                    d = md(sx, sy, rx, ry)
                    if best is None or d < best[0]:
                        best = (d, rx, ry)
        if best is not None:
            _, tx, ty = best

    best_move = (0, 0)
    best_val = None
    order = moves
    for dx, dy in order:
        nx, ny = int(sx + dx), int(sy + dy)
        if not valid(nx, ny):
            continue
        myd = md(nx, ny, tx, ty)
        oppd = md(ox, oy, tx, ty)
        dist_to_opp = md(nx, ny, ox, oy)
        if resources:
            val = (-myd * 4) + (oppd * 2) + dist_to_opp
        else:
            val = (dist_to_opp * 3) - md(nx, ny, tx, ty)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]