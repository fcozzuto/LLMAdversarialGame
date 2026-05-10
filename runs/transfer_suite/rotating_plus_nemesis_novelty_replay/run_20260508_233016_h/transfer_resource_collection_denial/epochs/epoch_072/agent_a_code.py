def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Drift toward center to reduce collision with sweeps
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            key = (dist(nx, ny, tx, ty), dist(nx, ny, ox, oy), nx, ny)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    # Pick a resource: prefer ones we can reach first; if tied, prefer those far from opponent.
    best_r = None
    best_key = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        secure = 0 if my_d <= op_d else 1
        key = (secure, my_d, -op_d, rx, ry)  # higher op_d better if equal/draw
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    # Step selection: go toward target, but keep some separation from opponent to resist sweep interference.
    best_move = None
    best_step_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_t = dist(nx, ny, tx, ty)
        d_to_o = dist(nx, ny, ox, oy)
        # If opponent is extremely close to the same target, prioritize running away slightly.
        op_close = 0 if dist(ox, oy, tx, ty) > 2 else 1
        key = (d_to_t, op_close * (-d_to_o) + (1 - op_close) * (-d_to_o), nx, ny)
        if best_step_key is None or key < best_step_key:
            best_step_key = key
            best_move = [dx, dy]

    return best_move if best_move else [0, 0]