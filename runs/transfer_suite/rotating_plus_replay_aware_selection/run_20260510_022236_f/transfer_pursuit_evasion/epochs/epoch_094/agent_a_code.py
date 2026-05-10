def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "escape", "flee"))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if (sx, sy) == (ox, oy):
        return [0, 0]

    def dist_cheb(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy

    def min_obst_manhattan(x, y):
        if not obstacles:
            return 10**9
        m = 10**9
        for px, py in obstacles:
            d = abs(px - x) + abs(py - y)
            if d < m:
                m = d
        return m

    corners = ((0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1))
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = dist_cheb(nx, ny)
        obst = min_obst_manhattan(nx, ny)
        corner_bias = abs(far_corner[0] - nx) + abs(far_corner[1] - ny)

        if is_evader:
            # maximize separation; stay away from obstacles; drift toward farthest corner
            score = (d, obst, corner_bias, -abs(nx - sx) - abs(ny - sy))
            if best is None or score > best_score:
                best_score = score
                best = (dx, dy)
        else:
            # minimize separation; avoid obstacles; prefer diagonal progress toward opponent
            step_pref = 1 if (dx != 0 and dy != 0) else 0
            score = (-d, obst, step_pref, -corner_bias)
            if best is None or score > best_score:
                best_score = score
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]