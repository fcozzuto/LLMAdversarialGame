def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            key = (cheb(nx, ny, tx, ty), -cheb(nx, ny, ox, oy), dx, dy)
            if best is None or key < best:
                best = key
        return [best[2], best[3]]

    # Resource-denial targeting: go for resources the opponent is closer to (so we can contest).
    best_res = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer high opponent advantage (do - ds), and low opponent distance (so it's relevant).
        key = (-(do - ds), do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_to_target = cheb(nx, ny, rx, ry)
        d_from_opp = cheb(nx, ny, ox, oy)
        # Reduce distance to target; if tied, increase separation from opponent; then deterministic dx/dy.
        key = (d_to_target, -d_from_opp, dx, dy)
        if best is None or key < best:
            best = key
    return [best[2], best[3]]