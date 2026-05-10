def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def kingd(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def corner_toward(x, y):
        return min(corners, key=lambda c: abs(x - c[0]) + abs(y - c[1]))

    def corner_away(x, y):
        return max(corners, key=lambda c: abs(x - c[0]) + abs(y - c[1]))

    self_role = (observation.get("self_role") or "").lower()
    pursuer = "pursuer" in self_role

    def predict_opponent_step(psx, psy):
        # assume opponent tries to keep its distance and drift to its far corner if possible
        corner = corner_away(ox, oy)
        best = None
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = ox + dx, oy + dy
            if not inside(nx, ny):
                continue
            d_corner = abs(nx - corner[0]) + abs(ny - corner[1])
            d_us = kingd(nx, ny, psx, psy)
            v = 1.6 * d_us + 0.05 * d_corner
            if v > bestv:
                bestv = v
                best = (nx, ny)
        return best if best is not None else (ox, oy)

    if pursuer:
        tx, ty = predict_opponent_step(sx, sy)
        best = None
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d_to_pred = kingd(nx, ny, tx, ty)
            d_to_real = kingd(nx, ny, ox, oy)
            # reward shrinking distance; penalize giving opponent slack to a corner
            opp_corner = corner_toward(ox, oy)
            opp_corner_slack = abs(nx - opp_corner[0]) + abs(ny - opp_corner[1])
            v = -2.3 * d_to_pred - 0.9 * d_to_real - 0.01 * opp_corner_slack
            if v > bestv:
                bestv = v
                best = (nx, ny)
        nx, ny = best if best is not None else (sx, sy)
        return [nx - sx, ny - sy]
    else:
        corner = corner_away(ox, oy)
        best = None
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d_us = kingd(nx, ny, ox, oy)
            d_corner = abs(nx - corner[0]) + abs(ny - corner[1])
            # prioritize staying far, then pushing toward safer corner
            v = 2.6 * d_us - 0.02 * d_corner
            if v > bestv:
                bestv = v
                best = (nx, ny)
        nx, ny = best if best is not None else (sx, sy)
        return [nx - sx, ny - sy]