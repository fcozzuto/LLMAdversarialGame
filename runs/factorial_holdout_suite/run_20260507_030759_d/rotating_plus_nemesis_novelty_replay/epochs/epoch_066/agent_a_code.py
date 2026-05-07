def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        cur_best = -10**18
        for rx, ry in resources:
            ts = cheb(nx, ny, rx, ry)
            to = cheb(ox, oy, rx, ry)
            # Prefer winning contest; tie-break toward sooner and closer to opponent's distance gap.
            gap = to - ts
            val = gap * 1000 - ts * 3
            if gap == 0:
                val -= cheb(nx, ny, ox, oy)  # if both can arrive, reduce proximity to opponent path pressure
            if val > cur_best:
                cur_best = val

        # Mild momentum: keep moving toward the best cell's direction if already aligned
        if cur_best > best_val:
            best_val = cur_best
            best_move = [dx, dy]

    return best_move