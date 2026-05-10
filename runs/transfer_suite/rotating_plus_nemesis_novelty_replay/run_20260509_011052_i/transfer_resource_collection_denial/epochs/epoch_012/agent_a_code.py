def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    target = None
    if resources:
        best = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = int(r[0]), int(r[1])
            dm = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            key = (dm - do, dm, -do)
            if best is None or key < best:
                best = key
                target = (rx, ry)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    if target is not None:
        tx, ty = target
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or blocked(nx, ny):
                continue
            score = man(nx, ny, tx, ty)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or blocked(nx, ny):
                continue
            score = -man(nx, ny, ox, oy)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]