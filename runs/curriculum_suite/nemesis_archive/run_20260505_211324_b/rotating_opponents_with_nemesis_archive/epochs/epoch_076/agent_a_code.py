def choose_move(observation):
    w = observation.get("grid_width")
    h = observation.get("grid_height")
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not isinstance(w, int) or not isinstance(h, int):
        return [0, 0]

    obs = set()
    for o in obstacles:
        try:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    def dist(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0:
            ax = -ax
        if ay < 0:
            ay = -ay
        return ax + ay

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_target = ((w - 1) // 2, (h - 1) // 2)
    if resources:
        best_d = 10**9
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) == 2:
                rx, ry = r[0], r[1]
                if isinstance(rx, int) and isinstance(ry, int) and 0 <= rx < w and 0 <= ry < h:
                    d = dist(sx, sy, rx, ry)
                    if d < best_d:
                        best_d = d
                        best_target = (rx, ry)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        dres = dist(nx, ny, best_target[0], best_target[1])
        dop = dist(nx, ny, ox, oy)
        score = (dres, -dop, -abs(nx - sx) - abs(ny - sy), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]