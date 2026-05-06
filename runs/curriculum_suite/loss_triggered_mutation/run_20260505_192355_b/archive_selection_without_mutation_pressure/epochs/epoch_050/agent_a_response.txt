def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_val = -10**18
    best_move = (0, 0)

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not ok(nx, ny):
            continue

        cur_best = -10**18
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            contested = 1.5 if od < sd else 1.0
            val = contested * (od - sd) - 0.01 * sd
            if val > cur_best:
                cur_best = val
        if cur_best > best_val:
            best_val = cur_best
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]