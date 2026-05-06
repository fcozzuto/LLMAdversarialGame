def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not res:
        best = min(moves, key=lambda t: (md(t[2], t[3], ox, oy), t[0], t[1]))
        return [int(best[0]), int(best[1])]

    best_key = None
    best_move = None
    for dx, dy, nx, ny in moves:
        # Find a resource where we can be competitive (reach no later than opponent if possible)
        best_comp = None
        best_all = None
        for rx, ry in res:
            d_us = md(nx, ny, rx, ry)
            d_opp = md(ox, oy, rx, ry)
            comp_key = (0 if d_us <= d_opp else 1, d_us - d_opp, d_us, -d_opp, rx, ry)
            all_key = (d_us, d_us - d_opp, -d_opp, rx, ry)
            if best_comp is None or comp_key < best_comp:
                best_comp = comp_key
            if best_all is None or all_key < best_all:
                best_all = all_key

        # Prefer competitive resources; otherwise fall back to closest-to-us
        key = (best_comp[0], best_comp[1], best_comp[2], best_comp[3], best_all[0], dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]