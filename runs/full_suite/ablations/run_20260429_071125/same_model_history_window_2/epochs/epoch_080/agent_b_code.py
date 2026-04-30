def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = []
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.append((x, y))
    obst = set(obstacles)

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def obs_pen(x, y):
        if not obstacles:
            return 0
        best = 10**9
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best:
                best = d
        if best >= 3:
            return 0
        return 6 - best  # 5..0

    if resources:
        target = min(resources, key=lambda t: (cheb(sx, sy, t[0], t[1]), t[0], t[1]))
        tx, ty = target
        best_score = -10**18
        best_move = [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obst:
                continue
            d = cheb(nx, ny, tx, ty)
            score = -d - obs_pen(nx, ny)
            if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
                best_score = score
                best_move = [dx, dy]
        return best_move

    # No resources: head toward opponent if safe, else wait.
    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        d = cheb(nx, ny, ox, oy)
        score = -d - obs_pen(nx, ny)
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]
    return best_move