def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obstacles.add((int(a[0]), int(a[1])))

    srole = str(observation.get("self_role", "")).lower()
    self_is_pursuer = ("purs" in srole) or ("chaser" in srole) or ("hunter" in srole) or ("pursuer" in srole)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    priority = {(0, 0): 0, (1, 0): 1, (-1, 0): 1, (0, 1): 2, (0, -1): 2, (1, 1): 3, (1, -1): 3, (-1, 1): 3, (-1, -1): 3}

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obstacle_pressure(x, y):
        # Penalize being near obstacles; stronger when acting as evader (escape from walls)
        pen = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                pen += 1
        for ax, ay in obstacles:
            if cheb(x, y, ax, ay) <= 2:
                pen += 2
        return pen

    def target_corners_score(x, y):
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        if self_is_pursuer:
            # As pursuer: go toward the corner farthest from opponent to reduce her options.
            tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        else:
            # As evader: go to the corner farthest from the opponent.
            tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        return cheb(x, y, tx, ty)

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        op_block = obstacle_pressure(nx, ny)
        tc = target_corners_score(nx, ny)
        if self_is_pursuer:
            score = d + 2.0 * op_block + 0.05 * tc
            # tie-break prefers lower priority (deterministic)
            if best is None or score < best_score or (score == best_score and priority[(dx, dy)] < priority[(best[0], best[1])]):
                best = (dx, dy); best_score = score
        else:
            score = -d + 2.0 * op_block + 0.03 * tc
            if best is None or score < best_score or (score == best_score and priority[(dx, dy)] < priority[(best[0], best[1])]):
                best = (dx, dy); best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]