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

    resources = []
    res_set = set()
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best_r = None
        best_v = 10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            v = ds - 0.55 * do
            if v < best_v:
                best_v = v
                best_r = (rx, ry)
        tx, ty = best_r

    def move_score(nx, ny):
        dres = cheb(nx, ny, tx, ty) if resources else cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
        dop = cheb(nx, ny, ox, oy)
        bonus = 8 if (nx, ny) in res_set else 0
        return bonus - dres + 0.12 * dop

    # Prefer direct step toward target; then choose best among valid moves deterministically.
    dx_dir = 0 if tx == sx else (1 if tx > sx else -1)
    dy_dir = 0 if ty == sy else (1 if ty > sy else -1)
    preferred = [(dx_dir, dy_dir), (dx_dir, 0), (0, dy_dir), (0, 0), (-dx_dir, 0), (0, -dy_dir)]
    checked = set()
    for dx, dy in preferred + deltas:
        if (dx, dy) in checked:
            continue
        checked.add((dx, dy))
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Evaluate locally (deterministic single-step).
        return [dx, dy]

    # Fallback: stay still.
    return [0, 0]