def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = [0, 0]
    best_val = -10**18 if pursuer else -10**18
    best_aux = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_op = cheb(nx, ny, ox, oy)

        if pursuer:
            if resources:
                d_res = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
                val = (-d_op) * 1000 + (-d_res)
                aux = (d_op, d_res, dx, dy)
            else:
                val = (-d_op) * 1000
                aux = (d_op, 0, dx, dy)
            if val > best_val or (val == best_val and (aux < best_aux if best_aux is not None else True)):
                best_val, best_aux, best = val, aux, [dx, dy]
        else:
            # Evader: maximize distance; if tie, move toward the farthest corner-like direction.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far_corner = max(cheb(nx, ny, cx, cy) for cx, cy in corners)
            if resources:
                d_res = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
                val = d_op * 1000 + far_corner - d_res
                aux = (-d_op, -far_corner, d_res, dx, dy)
            else:
                val = d_op * 1000 + far_corner
                aux = (-d_op, -far_corner, 0, dx, dy)
            if val > best_val or (val == best_val and (aux < best_aux if best_aux is not None else True)):
                best_val, best_aux, best = val, aux, [dx, dy]

    return [int(best[0]), int(best[1])]