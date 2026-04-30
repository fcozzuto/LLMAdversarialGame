def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Choose target resource where we have the biggest "reach advantage"
    best_t = None
    best_adv = -10**18
    for rx, ry in resources:
        dS = cheb(sx, sy, rx, ry)
        dO = cheb(ox, oy, rx, ry)
        adv = dO - dS
        # Tie-break toward nearer resources to us
        if adv > best_adv or (adv == best_adv and (best_t is None or dS < cheb(sx, sy, best_t[0], best_t[1]))):
            best_adv = adv
            best_t = (rx, ry)

    # If no resources visible, move toward opponent to contest; otherwise move toward target while worsening opponent distance
    if best_t is None:
        tx, ty = ox, oy
    else:
        tx, ty = best_t[0], best_t[1]

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best_move = None
    best_score = -10**18
    for dx, dy, nx, ny in legal:
        dS_after = cheb(nx, ny, tx, ty)
        dO = cheb(ox, oy, tx, ty)
        # Primary: gain on target
        score = (dO - dS_after)
        # Secondary: if target exists, reduce opponent closeness only when we are not already clearly leading
        if best_t is not None and dO <= dS_after:
            score += (cheb(ox, oy, sx, sy) - cheb(ox, oy, nx, ny)) * 0.5
        # Tertiary: avoid staying put when another move is equally good
        if dx == 0 and dy == 0:
            score -= 0.01
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]