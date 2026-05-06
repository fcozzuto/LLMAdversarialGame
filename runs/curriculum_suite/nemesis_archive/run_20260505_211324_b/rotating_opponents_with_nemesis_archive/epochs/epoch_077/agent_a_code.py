def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = p
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = []
    order = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        best = None
        bestv = -10**9
        for dx, dy, nx, ny in moves:
            v = md(nx, ny, ox, oy)  # pure avoidance
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best_target_adv = None
    best_target_score = -10**18
    my_close_any = False
    for rx, ry in resources:
        dm = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        adv = do - dm  # positive means I'm closer
        if adv > 0:
            my_close_any = True
        score = adv * 10 - dm * 0.2  # prefer strong advantage and closer
        if score > best_target_score:
            best_target_score = score
            best_target_adv = (rx, ry)

    if not my_close_any:
        # fallback: go for nearest resource (still deterministic)
        best_target = min(resources, key=lambda r: (md(sx, sy, r[0], r[1]), r[0], r[1]))
    else:
        best_target = best_target_adv

    rx, ry = best_target

    best = None
    bestv = -10**18
    for dx, dy, nx, ny in moves:
        dres = md(nx, ny, rx, ry)

        # Avoid opponent, but don't run into corners with no escape.
        dop = md(nx, ny, ox, oy)
        avoid = -4.0 / (1 + dop)

        # If opponent is very close, strongly prefer increasing distance.
        if dop <= 1:
            avoid = -10.0 + dop * 1.5

        # Small penalty for being in "trap" adjacent to opponent.
        trap_pen = 0.0
        if dop == 2 and (nx == ox or ny == oy):
            trap_pen = -1.0

        # If stepping onto a resource, big boost (resources presumably not obstacles).
        res_here = 1.0 if (nx, ny) in set(map(tuple, resources)) else 0.0
        # Make staying slightly less attractive to keep progress.
        stay_pen = -0.05 if (dx == 0 and dy == 0) else 0.0

        v = (-1.2 * dres) + avoid + trap_pen + (8.0 * res_here) + stay_pen
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]