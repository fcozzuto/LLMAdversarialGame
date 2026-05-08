def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = str(observation.get("self_role", "")).lower()
    pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit", "attacker"))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def corners():
        return [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    # If resources exist, prefer them as secondary objective for determinism
    resources = observation.get("resources", None) or []
    res_target = None
    if resources:
        best = None
        bestd = 10**9
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if d < bestd:
                bestd = d
                best = (int(rx), int(ry))
        res_target = best

    best_val = -10**18 if pursuer else 10**18
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_opp = cheb(nx, ny, ox, oy)
        # Pursuer: minimize distance (prefer getting to opponent).
        # Evader: maximize distance; also keep away from being trapped by obstacles by mildly favoring more free neighbors.
        free_neighbors = 0
        if not pursuer:
            for ddx, ddy in deltas:
                tx, ty = nx + ddx, ny + ddy
                if valid(tx, ty):
                    free_neighbors += 1

        if res_target is not None:
            d_res = cheb(nx, ny, res_target[0], res_target[1])
        else:
            d_res = 0

        # Small deterministic tie-breaks: grid bias favors moving toward "better" corner.
        c = corners()
        best_corner = c[0]
        best_corner_score = -10**9
        for cx, cy in c:
            score = cheb(cx, cy, ox, oy)  # farthest corner from opponent
            if score > best_corner_score:
                best_corner_score = score
                best_corner = (cx, cy)
        corner_push = cheb(nx, ny, best_corner[0], best_corner[1])

        if pursuer:
            val = -d_opp
            val += -0.01 * d_res
            val += 0.001 * corner_push
        else:
            val = d_opp
            val += 0.02 * free_neighbors
            val += 0.001 * corner_push
            val += -0.01 * d_res  # don't approach resource if it harms evasion

        if pursuer:
            if val > best_val + 1e-12 or (abs(val - best_val) <= 1e-12 and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)
        else:
            if val > best_val + 1e-12 or (abs(val - best_val) <= 1e-12 and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]