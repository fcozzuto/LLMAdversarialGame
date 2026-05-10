def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
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

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    evader = ("evader" in self_role) and ("evader" not in opp_role)
    pursuer = ("pursuer" in self_role) or not evader

    # candidate moves
    best_move = [0, 0]
    best_score = None

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # obstacle proximity (avoid bumping near obstacles)
    obs_list = list(obstacles)
    def obstacle_penalty(x, y):
        p = 0
        for ax, ay in obs_list:
            if ax == x and ay == y:
                return 10_000
            d2 = (ax - x) * (ax - x) + (ay - y) * (ay - y)
            if d2 <= 4:
                p += 5
            elif d2 <= 9:
                p += 2
        return p

    # boundary pressure (evader wants to stay away from corners; pursuer can allow slight cornering)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def center_score(x, y):
        return -((x - cx) * (x - cx) + (y - cy) * (y - cy))

    moves = (-1, 0, 1)
    for dx in moves:
        for dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d2 = dist2(nx, ny, ox, oy)
            pen = obstacle_penalty(nx, ny)
            if evader:
                # maximize distance; also prefer moves that don't hug obstacles and avoid corners
                # corners are low center_score; subtract obstacle_penalty from score
                score = d2 + 0.7 * center_score(nx, ny) - 1.5 * pen
                better = best_score is None or score > best_score
            else:
                # minimize distance; prioritize reducing separation and moving toward center a bit
                score = -d2 + 0.4 * center_score(nx, ny) - 1.2 * pen
                better = best_score is None or score > best_score

            if better:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]