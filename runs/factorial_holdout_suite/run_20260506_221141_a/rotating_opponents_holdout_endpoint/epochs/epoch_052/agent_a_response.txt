def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    # Choose target: closest to us; if tie, prefer farther from opponent.
    best = None
    bestd = None
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        if best is None or d < bestd:
            best = (rx, ry)
            bestd = d
        elif d == bestd:
            od = cheb(ox, oy, rx, ry)
            bo = cheb(ox, oy, best[0], best[1])
            if od > bo or (od == bo and (rx, ry) < best):
                best = (rx, ry)

    tx, ty = best

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy))

    if not candidates:
        return [0, 0]

    best_move = None
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Prefer getting closer to target, and (slightly) keep opponent at bay; tie-break deterministically.
        score = (-10 * d_self) + (0.05 * d_opp) - (0.001 * manh(nx, ny, tx, ty))
        if best_move is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]