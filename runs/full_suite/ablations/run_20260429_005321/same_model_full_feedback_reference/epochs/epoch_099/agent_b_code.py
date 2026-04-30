def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        for dx, dy in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Target resources by "tempo": how much faster we can reach them than the opponent.
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer positive gaps; tie-break by smaller self distance, then by smaller coords.
        gap = od - sd
        score = (gap, -sd, -cheb(sx, sy, rx, ry), -rx, -ry)
        if best is None or score > best[0]:
            best = (score, rx, ry)

    _, tx, ty = best
    # Choose one-step move that reduces distance to target; also avoid getting too close to obstacles.
    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_now = cheb(sx, sy, tx, ty)
        d_nxt = cheb(nx, ny, tx, ty)
        dd = d_now - d_nxt  # prefer improvement
        # Obstacle proximity penalty: count obstacles in 8-neighborhood (deterministic, small)
        prox = 0
        for ax, ay in obstacles:
            if cheb(nx, ny, ax, ay) <= 1:
                prox += 1
        # Also mildly discourage moving toward opponent (helps win races indirectly)
        opd = cheb(nx, ny, ox, oy)
        cur_opd = cheb(sx, sy, ox, oy)
        score = (dd, -prox, -opd, dx, dy)
        if best_move is None or score > best_move[0]:
            best_move = (score, dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]