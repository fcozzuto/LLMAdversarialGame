def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        key = (d_op - d_me, -d_me, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    if sx == rx and sy == ry:
        return [0, 0]

    def clamp_step(a, b):
        if b > a: return 1
        if b < a: return -1
        return 0

    target_step = (clamp_step(sx, rx), clamp_step(sy, ry))

    feasible = []
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            feasible.append((dx, dy, cheb(nx, ny, rx, ry)))
    if not feasible:
        return [0, 0]

    # Prefer moves matching target direction; then prefer smaller distance; tie-break deterministically.
    tx, ty = target_step
    best_m = None
    for dx, dy, d in feasible:
        dir_match = 1 if (dx == tx and dy == ty) else 0
        key = (dir_match, -d, -dx, -dy)
        if best_m is None or key > best_m[0]:
            best_m = (key, [dx, dy])
    return best_m[1]