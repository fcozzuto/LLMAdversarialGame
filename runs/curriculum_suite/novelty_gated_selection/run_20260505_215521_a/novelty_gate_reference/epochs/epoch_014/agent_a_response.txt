def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        bestv = 10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = cheb(nx, ny, tx, ty) + 0.1 * cheb(nx, ny, ox, oy)
            if v < bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_des = (sx, sy)
    best_score = -10**18

    # Pick a resource or an intercept cell if opponent is closer.
    for rx, ry in resources:
        d_s = cheb(sx, sy, rx, ry)
        d_o = cheb(ox, oy, rx, ry)
        if d_o < d_s:
            # Intercept roughly where opponent would step toward the resource.
            step_x = ox + (1 if rx > ox else -1 if rx < ox else 0)
            step_y = oy + (1 if ry > oy else -1 if ry < oy else 0)
            if not inb(step_x, step_y) or (step_x, step_y) in obstacles:
                des = (rx, ry)
            else:
                des = (step_x, step_y)
            score = 1.8 * (d_s - d_o) - 0.05 * cheb(step_x, step_y, sx, sy)
        else:
            des = (rx, ry)
            score = 2.0 * (d_o - d_s) - 0.01 * cheb(rx, ry, ox, oy)
        # Prefer higher score, break ties by closer to destination.
        if score > best_score or (score == best_score and cheb(sx, sy, des[0], des[1]) < cheb(sx, sy, best_des[0], best_des[1])):
            best_score = score
            best_des = des

    tx, ty = best_des
    # Greedy move toward the chosen destination with obstacle and proximity bias.
    best = [0, 0]
    bestv = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Main: distance to destination.
        v = cheb(nx, ny, tx, ty)
        # Secondary: avoid letting opponent come closer while we advance.
        v += 0.12 * cheb(nx, ny, ox, oy)
        # Tertiary: slight preference for moves that reduce destination distance monotonically.
        v += 0.01 * cheb(nx, ny, tx, ty)
        if v < bestv:
            bestv = v
            best = [dx, dy]
    return best