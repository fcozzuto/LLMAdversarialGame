def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = observation.get("obstacles", []) or []
    obs_set = set((int(p[0]), int(p[1])) for p in obstacles)

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or (("evad" in opp_role) and ("evad" not in self_role))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obs_set

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx*dx + dy*dy

    if pursuer:
        tx, ty = ox, oy
        # Greedy chase: minimize distance to target, tie-break by also preferring forward progress.
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = d2(nx, ny, tx, ty)
            progress = (d2(sx, sy, tx, ty) - d2(nx, ny, tx, ty))
            # Secondary tie-break: reduce distance to opponent along Chebyshev (faster capture alignment).
            align = max(abs(nx - tx), abs(ny - ty))
            key = (score, -progress, align, dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]
    else:
        # Evader: choose a corner that maximizes distance, but only among feasible local moves.
        # Target selection is deterministic (max lex over score).
        best_corner = None
        for cx, cy in corners:
            score = d2(ox, oy, cx, cy) + 2*d2(sx, sy, cx, cy)
            key = (-score, cx, cy)
            if best_corner is None or key < best_corner[0]:
                best_corner = (key, cx, cy)
        gx, gy = best_corner[1], best_corner[2]

        # Move selection: maximize distance from pursuer, and also head toward chosen goal.
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist_away = d2(nx, ny, ox, oy)
            dist_to_goal = d2(nx, ny, gx, gy)
            # Tie-breaks to avoid freezing: prefer reducing distance-to-goal slightly, then lexicographic by move.
            key = (-dist_away, dist_to_goal, dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]