def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = str(observation.get("self_role", "")).lower()
    pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit", "attacker"))

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),  (0, 0),  (0, 1),
              (1, -1),  (1, 0),  (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score_move(x, y):
        d = cheb(x, y, ox, oy)
        if pursuer:
            # Capture first (d==0), then minimize distance.
            # Tie-break: prefer staying closer to center to reduce wall trapping.
            center = (w / 2.0, h / 2.0)
            dist_center = cheb(x, y, center[0], center[1])
            return (-1e6 if d == 0 else -d * 100 - dist_center)
        else:
            # Evade: maximize distance; if equal, prefer moving away from obstacles by local clearance.
            # (more empty neighbors => larger value)
            if d == 0:
                return -1e6
            empty = 0
            for ddx, ddy in deltas:
                nx, ny = x + ddx, y + ddy
                if valid(nx, ny):
                    empty += 1
            return d * 100 + empty

    best_s = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        s = score_move(nx, ny)
        if best_s is None or s > best_s:
            best_s = s
            best_move = [dx, dy]
    return best_move if isinstance(best_move, list) else [0, 0]