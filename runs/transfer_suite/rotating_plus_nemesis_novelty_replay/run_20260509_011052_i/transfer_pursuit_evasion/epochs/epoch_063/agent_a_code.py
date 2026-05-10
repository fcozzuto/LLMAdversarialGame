def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    resources = observation.get("resources") or []
    if isinstance(resources, dict):
        resources = list(resources.values())
    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res_list.append((int(r[0]), int(r[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_dx, best_dy = 0, 0
    best_val = -10**18 if pursuer else 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = dist_cheb(nx, ny, ox, oy)
        if res_list:
            d_res = min(dist_cheb(nx, ny, rx, ry) for rx, ry in res_list)
        else:
            d_res = 0
        val = (-d_opp) + (0.2 if pursuer else -0.2) * d_res
        if not pursuer:
            val = (d_opp) + (0.2 if not pursuer else -0.2) * (-d_res)
        if (pursuer and val > best_val) or ((not pursuer) and val < best_val):
            best_val = val
            best_dx, best_dy = dx, dy
    return [int(best_dx), int(best_dy)]