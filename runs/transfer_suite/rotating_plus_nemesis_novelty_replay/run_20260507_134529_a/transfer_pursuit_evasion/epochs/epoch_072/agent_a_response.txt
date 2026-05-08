def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def score_move(nx, ny):
        d_opp = cheb(nx, ny, ox, oy)
        if is_evader:
            # Prefer being far; additionally drift toward a corner that is farthest from pursuer.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            target = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
            d_corner = cheb(nx, ny, target[0], target[1])
            # Break ties deterministically with corner distance and avoid nearby obstacles.
            near_obs = 0
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                if (nx + dx, ny + dy) in obstacles:
                    near_obs += 1
            return (d_opp, d_corner, -near_obs)
        else:
            # Pursuer: minimize distance to opponent; avoid obstacle adjacency slightly.
            near_obs = 0
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                if (nx + dx, ny + dy) in obstacles:
                    near_obs += 1
            return (-d_opp, -near_obs)

    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        key = score_move(nx, ny)
        if best_key is None:
            best_key, best_move = key, [dx, dy]
        else:
            if is_evader:
                if key > best_key:
                    best_key, best_move = key, [dx, dy]
            else:
                if key > best_key:
                    best_key, best_move = key, [dx, dy]

    return best_move