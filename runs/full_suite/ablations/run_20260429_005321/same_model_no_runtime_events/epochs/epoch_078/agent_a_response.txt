def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not valid(sx, sy):
        for dx, dy in sorted(dirs):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        best = None
        best_key = None
        for x, y in resources:
            md = cheb(sx, sy, x, y)
            od = cheb(ox, oy, x, y)
            advantage = od - md  # bigger is better: opponent farther than us
            key = (-(advantage), md, x, y)  # minimize (-advantage), md, then coord
            if best_key is None or key < best_key:
                best_key = key
                best = (x, y)
        tx, ty = best
    else:
        tx, ty = (w - 1) if ox == sx else ox, (h - 1) if oy == sy else oy
        # fallback: move toward opponent to contest space deterministically

    # Choose move that gets closer (chebyshev) to target; tie-break by moving toward opponent and then coords.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        to_op_prev = cheb(sx, sy, ox, oy)
        to_op_new = cheb(nx, ny, ox, oy)
        # Prefer smaller distance to target; then reduce distance to opponent; then deterministic
        val = (d, to_op_new - to_op_prev, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]