def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()

    i_am_pursuer = ("purs" in self_role) or ("chase" in self_role) or ("hunter" in self_role)
    if not i_am_pursuer:
        if ("purs" in opp_role) or ("chase" in opp_role) or ("hunter" in opp_role):
            i_am_pursuer = False
        else:
            i_am_pursuer = ("evad" not in self_role) and ("escap" not in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def walliness(x, y):
        return min(x, w - 1 - x) + min(y, h - 1 - y)

    if not i_am_pursuer:
        # Evader: move to maximize distance; if blocked, slide along best axis.
        best = None
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            s = dist2(nx, ny, ox, oy)
            # Prefer going toward farther corner relative to pursuer when possible
            tc = max(corners, key=lambda p: dist2(p[0], p[1], sx, sy))
            s += 0.05 * dist2(nx, ny, tc[0], tc[1])
            s += 0.02 * (walliness(nx, ny) * -1)
            if s > best_score or (s == best_score and (dx, dy) < best):
                best_score = s
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    # Pursuer: greedy minimize distance; additionally bias toward a target corner and away from obstacles' immediate proximity.
    target_corner = min(corners, key=lambda p: dist2(p[0], p[1], ox, oy))
    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        # Score: lower distance is better, so use negative.
        s = -d
        # Corner pressure: reducing distance to the corner relative to current
        s += 0.03 * (-dist2(nx, ny, target_corner[0], target_corner[1]))
        # Avoid being boxed: reward moves with more valid neighbors
        deg = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if valid(tx, ty):
                deg += 1
        s += 0.08 * deg
        # Small tie-breakers toward staying off obstacles: penalize closeness to obstacle cells
        if obstacles:
            min_obs = None
            for px, py in obstacles:
                q = dist2(nx, ny, px, py)
                if min_obs is None or q < min_obs:
                    min_obs = q
            if min_obs is not None:
                s += 0.01 * min_obs
        if s > best_score or (s == best_score and (dx, dy) < best):
            best_score = s
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]