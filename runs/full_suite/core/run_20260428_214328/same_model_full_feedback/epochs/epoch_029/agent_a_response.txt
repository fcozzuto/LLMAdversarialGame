def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obstacle_pressure(x, y):
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if (nx, ny) in obstacles:
                    p += 1
        return p

    # Pick best target: beat opponent on distance; if all close, still prefer high advantage
    if resources:
        best = resources[0]
        best_key = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Key: prioritize resources we can reach earlier; also account for being closer than opponent
            key = (od - sd, -sd, -cheb(sx, sy, rx, ry) + 0.01 * (rx + ry))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        # No visible resources: move to center to avoid corners getting trapped
        cx, cy = w // 2, h // 2
        tx, ty = cx, cy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    # Deterministic move choice: minimize target distance, then maximize relative advantage, penalize obstacle pressure
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Encourage moving if we can reduce distance more than opponent's relative edge; avoid obstacle-adjacent squares
        rel = (opd - myd)
        score = (rel * 1000) - myd * 10 - obstacle_pressure(nx, ny) * 2
        # Slight tie-break to keep movement stable: prefer staying if equal
        if score == score and (best_score is None or score > best_score or (score == best_score and (dx, dy) == (0, 0))):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]