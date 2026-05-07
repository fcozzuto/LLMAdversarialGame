def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    rs = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y):
                rs.append((x, y))
    if not rs:
        return [0, 0]

    best = None
    best_key = None
    for tx, ty in rs:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # If we can beat them to it, prefer smallest self distance.
        # Otherwise, deny by preferring resources they are farthest from.
        if sd < od:
            key = (0, sd, od, tx, ty)
        else:
            key = (1, -od, sd, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(nx, ny, ox, oy)  # just a stability term
        # Prefer reducing distance to target; if tied, prefer moves that keep opponent farther.
        score = (sd2, -od2, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]