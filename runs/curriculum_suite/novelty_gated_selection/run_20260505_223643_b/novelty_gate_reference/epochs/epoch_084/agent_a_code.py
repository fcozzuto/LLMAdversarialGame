def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def step_towards(tx, ty):
        cx, cy = sx, sy
        dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
        best = None
        for dx, dy in dirs:
            nx, ny = cx + dx, cy + dy
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if best is None or d < best[0] or (d == best[0] and (dx, dy) < best[1]):
                best = (d, (dx, dy))
        return best[1] if best else (0, 0)

    center = (w // 2, h // 2)
    # Anticipatory intercept: go one step toward opponent's direction to center if it yields advantage.
    icx, icy = ox, oy
    if icx < center[0]: icx += 1
    elif icx > center[0]: icx -= 1
    if icy < center[1]: icy += 1
    elif icy > center[1]: icy -= 1
    intercept = (icx, icy) if inb(icx, icy) else (sx, sy)

    best_t = None
    best_val = None
    # Resource contest heuristic: maximize (opp_time - my_time), then closeness to center as tie-break.
    for rx, ry in sorted(resources):
        my_t = cheb(sx, sy, rx, ry)
        op_t = cheb(ox, oy, rx, ry)
        val = op_t - my_t
        cdist = cheb(rx, ry, center[0], center[1])
        cand = (val, -cdist, my_t, rx, ry)
        if best_val is None or cand > best_t:
            best_t = cand
    # Decide between intercept and best resource (intercept only if it increases advantage).
    target = (int(best_t[3]), int(best_t[4]))
    res_adv = best_t[0]
    int_adv = cheb(sx, sy, intercept[0], intercept[1]) - cheb(ox, oy, intercept[0], intercept[1])
    # int_adv is my_time - opp_time; want it negative for advantage, convert to (opp - my).
    if intercept != (sx, sy):
        int_score = -int_adv
        if int_score > res_adv:
            target = intercept

    return list(step_towards(target[0], target[1]))