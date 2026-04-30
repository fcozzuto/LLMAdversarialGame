def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        diff = opd - myd
        key = (diff, -myd, -(rx + 17 * ry))
        if best_key is None or key > best_key:
            best_key, best = key, (rx, ry)

    tx, ty = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            return (-10**9, 0)
        if (nx, ny) in obstacles:
            return (-10**9, 0)
        d_to = cheb(nx, ny, tx, ty)
        d_block = cheb(ox, oy, nx, ny)
        return (d_to, -d_block)

    # Prefer moves that reduce our distance most, and keep us farther from opponent.
    best_m = (0, 0)
    best_s = None
    for dx, dy in moves:
        s = score_move(dx, dy)
        if best_s is None or s < best_s:
            best_s, best_m = s, (dx, dy)
    return [int(best_m[0]), int(best_m[1])]