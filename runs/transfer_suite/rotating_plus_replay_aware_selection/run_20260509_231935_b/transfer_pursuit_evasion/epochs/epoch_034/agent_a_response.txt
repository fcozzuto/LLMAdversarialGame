def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    sr = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in sr) or ("chas" in sr)  # robust to naming

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        # also discourage moves that get closer to obstacles (helps with wall runner)
        obst_pen = 0
        for bx, by in obs:
            dd = abs(nx - bx) + abs(ny - by)
            if dd == 0:
                obst_pen += 1000
            else:
                obst_pen += 1.0 / dd

        if is_pursuer:
            # minimize distance to evader, then avoid obstacles
            score = (-d) - 0.05 * obst_pen
            better = (best_score is None) or (score > best_score)
        else:
            # maximize distance from pursuer, then avoid obstacles and prefer corner pressure
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            corner_bonus = max(dist2(nx, ny, cx, cy) for cx, cy in corners)
            score = d + 0.02 * corner_bonus - 0.05 * obst_pen
            better = (best_score is None) or (score > best_score)

        if better:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]