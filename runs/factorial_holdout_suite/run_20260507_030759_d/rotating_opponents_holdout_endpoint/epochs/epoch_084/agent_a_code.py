def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    my_corner = (0, 0)
    if (sx, sy) != my_corner:
        if sx == w - 1 and sy == h - 1:
            my_corner = (w - 1, h - 1)

    if resources:
        best_t = None
        best_key = None
        for rx, ry in resources:
            if not isinstance(rx, int) or not isinstance(ry, int):
                continue
            dme = dist((sx, sy), (rx, ry))
            doe = dist((ox, oy), (rx, ry))
            # Prefer resources we can arrive sooner; break ties by farther (less contested) and then coords.
            key = (-(dme - doe), dme + doe, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (rx, ry)
        tx, ty = best_t if best_t is not None else resources[0]
    else:
        # No known resources: head toward the geometric center-ish, deterministic.
        tx, ty = (w // 2, h // 2)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dm = dist((nx, ny), (tx, ty))
        do = dist((nx, ny), (ox, oy))
        # Higher is better: minimize distance to target, discourage moving too close to opponent.
        score = (dm * 1000 - do, dm, -dx, -dy, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]