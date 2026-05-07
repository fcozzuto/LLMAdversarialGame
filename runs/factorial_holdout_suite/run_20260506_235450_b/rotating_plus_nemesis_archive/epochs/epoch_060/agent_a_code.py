def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_t = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obs:
            continue
        my = dist(sx, sy, rx, ry)
        op = dist(ox, oy, rx, ry)
        # First: can reach strictly before opponent; otherwise: maximize advantage (op - my)
        key = (0 if my < op else 1, -(op - my), my, (rx + 2 * ry) % 3, rx, ry)
        if best_t is None or key < best_t[0]:
            best_t = (key, (rx, ry))
    if best_t is None:
        tx, ty = (w // 2, h // 2)
    else:
        tx, ty = best_t[1]

    # Choose move that is valid and most reduces distance to target, deterministic tie-break.
    best_m = None
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = dist(nx, ny, tx, ty)
        if best_d is None or nd < best_d or (nd == best_d and (dx, dy) < best_m):
            best_d = nd
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]