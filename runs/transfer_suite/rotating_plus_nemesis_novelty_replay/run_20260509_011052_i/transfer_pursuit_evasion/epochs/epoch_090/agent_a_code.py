def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set(tuple(p) for p in obstacles)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    def cheb(x, y, a, b):
        dx = x - a
        dy = y - b
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    role = observation.get("self_role", "pursuer")
    pursue = (role.lower() != "evader")
    center_x = (w - 1) / 2.0
    center_y = (h - 1) / 2.0
    best_dx, best_dy = 0, 0
    best_score = -10**18 if pursue else 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        moved = 1 if (dx != 0 or dy != 0) else 0
        cdx = abs(nx - center_x)
        cdy = abs(ny - center_y)
        cen_dist = cdx + cdy
        # Greedy pursuit/evasion with deterministic tie-break toward center.
        if pursue:
            score = -dist * 100000 + moved * 10 - cen_dist
            if score > best_score:
                best_score = score
                best_dx, best_dy = dx, dy
        else:
            score = dist * 100000 + moved * 10 - cen_dist
            if score > best_score:
                best_score = score
                best_dx, best_dy = dx, dy
    return [int(best_dx), int(best_dy)]