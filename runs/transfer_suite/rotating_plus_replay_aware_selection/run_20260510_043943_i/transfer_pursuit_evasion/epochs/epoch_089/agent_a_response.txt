def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_pen(nx, ny):
        if (nx, ny) in obstacles:
            return 10**6
        p = 0
        for ax, ay in obstacles:
            d = cheb(nx, ny, ax, ay)
            if d == 0:
                return 10**6
            if d == 1:
                p += 7
            elif d == 2:
                p += 3
        return p

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        pen = obst_pen(nx, ny)
        if pen >= 10**6:
            continue

        dist = cheb(nx, ny, ox, oy)
        dcenter = abs(nx - cx) + abs(ny - cy)

        if is_evader:
            # primary: maximize distance; secondary: avoid obstacles and don't hug corners too hard
            score = (-dist) + 0.02 * dcenter + 0.8 * pen
            # we minimize score
            pick_better = best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move)
        else:
            # primary: minimize distance; secondary: avoid obstacles and keep some center pressure
            score = dist + 0.02 * dcenter + 0.8 * pen
            # we minimize score
            pick_better = best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move)

        if pick_better:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]