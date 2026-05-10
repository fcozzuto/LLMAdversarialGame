def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d(a, b):
        # Chebyshev distance (diagonal moves allowed)
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cells = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                cells.append((x, y))
    if not cells:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_t = None
    best = None
    for t in cells:
        sd = d((sx, sy), t)
        od = d((ox, oy), t)
        # Prefer resources where we are sooner; otherwise still progress, but reduce contention.
        margin = od - sd
        quad = (t[0] >= w // 2, t[1] >= h // 2)
        dist_op = od
        cand = (margin, -sd, -dist_op, quad)
        if best is None or cand > best:
            best = cand
            best_t = t

    tx, ty = best_t
    # If we can't get any positive margin, still head toward the best target but with slight contention bias:
    # move that increases separation from opponent direction if possible.
    best_move = (0, 0)
    best_m = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sd2 = d((nx, ny), (tx, ty))
        od2 = d((nx, ny), (ox, oy))
        # Primary: reduce distance to target. Secondary: increase distance from opponent.
        cand = (-sd2, od2, dx, dy)
        if best_m is None or cand > best_m:
            best_m = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]