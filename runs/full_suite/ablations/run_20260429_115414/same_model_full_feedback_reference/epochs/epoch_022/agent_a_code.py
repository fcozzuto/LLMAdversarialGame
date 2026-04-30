def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1,  0), (0,  0), (1,  0),
             (-1,  1), (0,  1), (1,  1)]

    def in_bounds(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    def manh(x, y, a, b):
        dx = x - a
        if dx < 0: dx = -dx
        dy = y - b
        if dy < 0: dy = -dy
        return dx + dy

    resources = observation.get("resources") or []
    best_targets = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                best_targets.append((x, y))
    if not best_targets:
        best_targets = [(ox, oy)]

    # Choose target that is closer to us (tie-break toward opponent distance to deny).
    best_t = None
    best_sc = None
    for tx, ty in best_targets:
        d_me = manh(sx, sy, tx, ty)
        d_op = manh(ox, oy, tx, ty)
        sc = (d_me, -d_op, tx, ty)
        if best_sc is None or sc < best_sc:
            best_sc = sc
            best_t = (tx, ty)

    tx, ty = best_t
    # Evaluate candidate moves with simple deterministic heuristic.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d_to = manh(nx, ny, tx, ty)
        d_op = manh(nx, ny, ox, oy)
        # Prefer getting closer to target and farther from opponent (deterministic tie-break).
        val = (d_to, -d_op, nx, ny, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]