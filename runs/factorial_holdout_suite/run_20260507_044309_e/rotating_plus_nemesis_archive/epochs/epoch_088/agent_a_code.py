def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def line_bias(x, y):
        # Heuristic vs sweep_rows: reward blocking same-row race (our move toward resources on opponent row).
        return 1 if y == oy else 0

    # Pick the resource where we are relatively closer than opponent, but also avoid hopeless long distances.
    best_r = resources[0]
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Key: maximize advantage, then minimize our distance, then deterministic by coordinates.
        key = (od - sd, -sd, -line_bias(rx, ry), -rx - 100 * ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    best_m = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Prefer steps that reduce our distance to target and slightly increase separation from opponent.
        sep = cheb(nx, ny, ox, oy)
        # Also penalize moving onto opponent row if it helps them contest many cells (small deterministic bias).
        row_pen = 1 if ny == oy and (cheb(nx, ny, tx, ty) > 0) else 0
        val = (-nd, -sep, row_pen, dx * 10 + dy)  # earlier lexicographic tie-break
        if best_val is None or val < best_val:
            best_val = val
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]