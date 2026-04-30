def choose_move(observation):
    w = observation.get("grid_width", 0) or 0
    h = observation.get("grid_height", 0) or 0
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    targets = []
    for r in resources:
        rx, ry = r
        if not inside(rx, ry):
            continue
        opd = cheb(ox, oy, rx, ry)
        myd = cheb(sx, sy, rx, ry)
        # Prefer resources where we are not worse and can potentially capture soon
        if opd <= 2 and myd <= opd + 1:
            targets.append((myd, opd, rx, ry))
    if targets:
        targets.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
        tx, ty = targets[0][2], targets[0][3]
    elif resources:
        best = None
        for r in resources:
            rx, ry = r
            if not inside(rx, ry):
                continue
            d = cheb(sx, sy, rx, ry)
            if best is None or d < best[0] or (d == best[0] and (rx, ry) < (best[1], best[2])):
                best = (d, rx, ry)
        tx, ty = best[1], best[2]
    else:
        # No resources: move toward center, avoiding obstacles
        tx, ty = (w - 1) // 2, (h - 1) // 2

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        # If opponent is closer to the target, prefer moves that reduce our distance gap
        opp_gap = cheb(ox, oy, tx, ty) - d_to
        # Smaller is better: prioritize capturing (min d_to), then maximize opp_gap, then deterministic
        score = (d_to, -opp_gap, abs(nx - (w - 1) // 2) + abs(ny - (h - 1) // 2), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
    if best_move is None:
        return [0, 0]
    return best_move