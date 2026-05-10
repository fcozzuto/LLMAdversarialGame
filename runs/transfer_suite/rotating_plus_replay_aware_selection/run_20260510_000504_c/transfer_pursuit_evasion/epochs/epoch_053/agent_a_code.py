def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]

    obstacles = []
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.append((int(x), int(y)))
        except:
            pass

    self_role = str(observation.get("self_role", "") or "").lower()
    opponent_role = str(observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("hunter" in self_role) or ("evad" in opponent_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def obs_clear(nx, ny):
        if not obstacles:
            return 4
        dmin = 10**9
        for bx, by in obstacles:
            d = abs(nx - bx) + abs(ny - by)
            if d < dmin:
                dmin = d
        return dmin

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    target_corner = None
    if not is_pursuer:
        best = None
        for cx, cy in corners:
            dist_to_obs = min((abs(cx - bx) + abs(cy - by)) for (bx, by) in obstacles) if obstacles else 10
            val = (md(cx, cy, ox, oy), dist_to_obs)
            if best is None or val > best:
                best = val
                target_corner = (cx, cy)
        if target_corner is None:
            target_corner = corners[0]
    else:
        target_corner = (ox, oy)

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = int(sx) + dx, int(sy) + dy
        # Clamp to grid (engine would keep in place on invalid; clamp makes deterministic tie-break consistent)
        if nx < 0: nx = 0
        if nx >= w: nx = w - 1
        if ny < 0: ny = 0
        if ny >= h: ny = h - 1

        if is_pursuer:
            prog = -md(nx, ny, ox, oy)
        else:
            prog = md(nx, ny, ox, oy)
            # also bias toward a safer corner
            prog += 0.15 * md(nx, ny, target_corner[0], target_corner[1])

        clear = obs_clear(nx, ny)
        # Avoid moving into/near obstacles; if stuck, still keep deterministic progress
        obstacle_pen = 0
        if obstacles:
            obstacle_pen = -2.5 / (1 + clear)
        corner_tight = -0.01 * md(nx, ny, target_corner[0], target_corner[1])

        score = prog + 0.6 * clear + obstacle_pen + corner_tight

        # Deterministic tie-break: prefer smaller dx, then smaller dy, then higher score
        cand = (score, -abs(dx) - abs(dy), -dx, -dy)
        if best_score is None or cand > best_score:
            best_score = cand
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]