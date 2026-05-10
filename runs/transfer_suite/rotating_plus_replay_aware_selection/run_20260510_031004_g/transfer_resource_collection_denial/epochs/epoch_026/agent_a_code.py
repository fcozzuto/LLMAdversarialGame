def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            obstacles.add((x, y))
        except:
            pass

    resources = []
    for p in (observation.get("resources") or []):
        try:
            resources.append((int(p[0]), int(p[1])))
        except:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    best = None
    best_t = resources[0]
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        margin = od - sd  # prefer where we are closer than opponent
        key = (-(margin), sd, rx, ry)  # minimize margin-neg (i.e., maximize margin)
        if best is None or key < best:
            best = key
            best_t = (rx, ry)

    tx, ty = best_t
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_d = None
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        # tie-break deterministically: closer, then move order preference via key
        key = (d, abs(dx) + abs(dy), dx, dy)
        if best_d is None or key < best_key:
            best_d = d
            best_key = key
            best_move = (dx, dy)

    if best_move == (0, 0):
        # If all moves blocked, stay (engine keeps in place on invalid)
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]