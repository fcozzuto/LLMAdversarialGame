def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_ob_pen(x, y):
        pen = 0
        for (oxx, oyy) in obstacles:
            if abs(oxx - x) <= 1 and abs(oyy - y) <= 1:
                pen += 1
        return pen

    best_t = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (do - ds, -ds, -(rx + ry * 7))  # favor race wins, then closer, then deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = [0, 0]
    best_s = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds_after = cheb(nx, ny, rx, ry)
        do_same = cheb(ox, oy, rx, ry)
        # prefer move that improves race margin and reduces distance; also avoid obstacles strongly
        margin = do_same - ds_after
        score = (margin * 100) - ds_after * 5 - adj_ob_pen(nx, ny) * 20
        # small preference to progress toward target direction deterministically
        score += -(abs((nx - rx)) + abs((ny - ry))) * 0.1
        if best_s is None or score > best_s:
            best_s = score
            best_m = [dx, dy]

    return best_m