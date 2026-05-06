def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Prefer resources where we are relatively closer than opponent (intercept pressure),
    # but also prefer overall closeness to finish.
    best = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        rel = sd - (od * 1.2)  # intercept advantage
        val = (rel, sd, rx, ry)
        if best is None or val < best:
            best = val
            target = (rx, ry)

    rx, ry = target
    best_move = (0, 0)
    best_score = None

    # Greedy step selection with obstacle avoidance.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        self_d = md(nx, ny, rx, ry)
        opp_d = md(ox, oy, rx, ry)
        # Encourage reducing distance to target; discourage moves that allow opponent to have much better relative access.
        rel = self_d - (opp_d * 1.0)
        # If stepping into a cell that is adjacent to many obstacles, penalize slightly for robustness.
        adj_obs = 0
        for ax, ay in moves:
            tx, ty = nx + ax, ny + ay
            if (tx, ty) in obstacles:
                adj_obs += 1
        score = (rel, self_d, adj_obs, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]