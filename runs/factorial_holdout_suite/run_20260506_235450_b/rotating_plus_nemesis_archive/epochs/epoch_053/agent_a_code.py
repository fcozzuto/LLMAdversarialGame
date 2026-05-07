def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(ax, ay, bx, by):
        ax = ax - bx
        if ax < 0:
            ax = -ax
        ay = ay - by
        if ay < 0:
            ay = -ay
        return ax + ay

    # Choose target: nearest resource if any, else move toward opponent.
    if resources:
        best_t = None
        best_d = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            d = dist(sx, sy, rx, ry)
            if best_d is None or d < best_d or (d == best_d and (rx, ry) < best_t):
                best_d = d
                best_t = (rx, ry)
        tx, ty = best_t
        # If already on a resource, stay (deterministic).
        if (sx, sy) == (tx, ty):
            return [0, 0]
    else:
        tx, ty = ox, oy

    # One-step greedy: minimize distance to target; if tied, prefer increasing distance from opponent.
    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to = dist(nx, ny, tx, ty)
        d_op = dist(nx, ny, ox, oy)
        # Favor smaller d_to; then larger d_op; then deterministic ordering.
        key = (d_to, -d_op, dx, dy)
        if best is None or key < best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]