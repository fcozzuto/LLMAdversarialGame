def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def step_options():
        res = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    res.append((0, 0))
                else:
                    nx, ny = sx + dx, sy + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                        res.append((dx, dy))
        # deterministic preference order (closest to main diagonal first)
        res.sort(key=lambda t: (-(abs(t[0]) + abs(t[1]) == 2), -(t[0] == 0 and t[1] == 0), abs(t[0]) + abs(t[1])))
        return res

    # Pick target with best advantage (opponent farthest relative to us), tie-break by smaller our distance and then coordinates.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        advantage = od - sd
        key = (-advantage, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    best_move = (0, 0)
    best_eval = None
    for dx, dy in step_options():
        nx, ny = sx + dx, sy + dy
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        # Evaluate next-step advantage and distance reduction to target.
        adv2 = od2 - sd2
        # tie-break: reduce our distance first, then prefer moves that increase advantage, then deterministic ordering.
        eval_key = (-adv2, sd2, nx, ny)
        if best_eval is None or eval_key < best_eval:
            best_eval = eval_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]