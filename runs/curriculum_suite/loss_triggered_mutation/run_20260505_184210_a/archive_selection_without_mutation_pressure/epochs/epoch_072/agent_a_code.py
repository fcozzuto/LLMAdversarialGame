def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))

    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    if not resources:
        # Retreat from opponent and avoid obstacles by picking safest legal move
        best = None
        for dx, dy, nx, ny in legal:
            opp = md(nx, ny, ox, oy)
            key = (-opp, dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Denial-aware: prioritize resources where we can beat (or deny) opponent's arrival.
    best = None
    for dx, dy, nx, ny in legal:
        best_delta = None
        best_self = 10**9
        best_opp = 10**9
        for rx, ry in resources:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            delta = ds - do  # smaller (more negative) means we are closer/earlier
            if best_delta is None or delta < best_delta or (delta == best_delta and (ds < best_self or (ds == best_self and do < best_opp))):
                best_delta = delta
                best_self = ds
                best_opp = do
        # Prefer beating opponent; if tied, prefer closer self and farther from opponent globally.
        glob_opp = md(nx, ny, ox, oy)
        key = (best_delta, best_self, -glob_opp, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]] if best else [0, 0]