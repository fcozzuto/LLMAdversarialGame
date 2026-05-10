def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for it in (observation.get("obstacles") or []):
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    self_role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in self_role) or ("escape" in self_role) or ("runner" in self_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    obs_list = list(obstacles)

    def min_obs_dist(x, y):
        if not obs_list:
            return 999
        best = 999
        for ax, ay in obs_list:
            d = cheb(x, y, ax, ay)
            if d < best:
                best = d
                if best == 0:
                    return 0
        return best

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy)) if is_evader else min(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    best_move = (0, 0)
    best_val = -10**9 if is_evader else 10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_opp = cheb(nx, ny, ox, oy)
        d_to_corner = cheb(nx, ny, best_corner[0], best_corner[1])
        o_dist = min_obs_dist(nx, ny)
        # Evader: maximize distance to opponent, also keep away from obstacles; prefer going to farthest corner.
        # Pursuer: minimize distance to opponent, while staying away from obstacles; prefer toward corner only as tie-break.
        if is_evader:
            val = d_to_opp * 10 - (8 - min(8, o_dist)) + d_to_corner * 0.1
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)
        else:
            val = d_to_opp * -10 - (8 - min(8, o_dist)) - d_to_corner * 0.1
            if val < best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]