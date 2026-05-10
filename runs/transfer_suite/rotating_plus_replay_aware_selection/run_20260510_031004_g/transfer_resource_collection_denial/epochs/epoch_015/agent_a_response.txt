def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def opp_step_toward(tx, ty):
        best = None
        for dx, dy in deltas:
            nx, ny = ox + dx, oy + dy
            if not inb(nx, ny):
                nx, ny = ox, oy
            d = cheb(nx, ny, tx, ty)
            key = (d, nx, ny)
            if best is None or key < best[0]:
                best = (key, nx, ny)
        return best[1], best[2]

    res = [(int(p[0]), int(p[1])) for p in resources]
    best_move = [0, 0]
    best_score = None

    for dx0, dy0 in deltas:
        nx, ny = sx + dx0, sy + dy0
        if not inb(nx, ny):
            nx, ny = sx, sy

        move_score = None
        for tx, ty in res:
            sd = cheb(nx, ny, tx, ty)
            onx, ony = opp_step_toward(tx, ty)
            od = cheb(onx, ony, tx, ty)

            collect_bonus = 2000 if (nx == tx and ny == ty) else 0
            win_bias = (od - sd) * 100
            s = collect_bonus + win_bias - sd

            if move_score is None or s > move_score:
                move_score = s

        if best_score is None or move_score > best_score:
            best_score = move_score
            best_move = [dx0, dy0]

    return best_move