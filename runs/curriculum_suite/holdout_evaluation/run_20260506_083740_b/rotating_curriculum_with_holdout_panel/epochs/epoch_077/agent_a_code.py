def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    ob = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                ob.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    resources = observation.get("resources", []) or []

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_score = None
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        sc = (sd - od) + (0.3 * sd)  # prioritize not losing race; break ties by being closer
        if best_score is None or sc < best_score:
            best_score = sc
            best = (rx, ry)

    tx, ty = best if best is not None else (ox, oy)

    curd = md(sx, sy, tx, ty)
    best_move = None
    best_dist = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = md(nx, ny, tx, ty)
        if d < curd or best_move is None:
            if best_dist is None or d < best_dist:
                best_dist = d
                best_move = [dx, dy]

    if best_move is not None:
        return best_move

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]

    return [0, 0]