def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    target = None

    if resources:
        opp_better = []
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if do <= ds:  # opponent is at least as close
                opp_better.append((ds, rx, ry))
        if opp_better:
            opp_better.sort(key=lambda t: (t[0], t[1], t[2]))
            target = (opp_better[0][1], opp_better[0][2])
        else:
            scored = []
            for rx, ry in resources:
                ds = cheb(sx, sy, rx, ry)
                scored.append((ds, rx, ry))
            scored.sort(key=lambda t: (t[0], t[1], t[2]))
            target = (scored[0][1], scored[0][2])

        tx, ty = target
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            score = -cheb(nx, ny, tx, ty)  # maximize closeness
            if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
                best_score = score
                best = (dx, dy)
        if best is not None:
            return [int(best[0]), int(best[1])]

    # Fallback: move away from opponent deterministically
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        score = cheb(nx, ny, ox, oy)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]