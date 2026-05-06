def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if w <= 0 or h <= 0:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        for dx, dy in [(1, 1), (1, 0), (0, 1), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # Pick resource that maximizes "intercept advantage": opponent is relatively farther than us.
    best = None
    bestv = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer earlier capture; if tie, prefer closer to center.
        center_bias = - (abs(rx - cx) + abs(ry - cy)) * 0.01
        v = (do - ds) * 10.0 + (-ds) * 1.0 + center_bias
        if v > bestv:
            bestv = v
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Greedy step toward target, avoiding obstacles; deterministic tie-break.
    best_move = (0, 0)
    best_score = (10**18, -10**18, 10**18)  # (dist, -progress, lex)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nds = cheb(nx, ny, tx, ty)
        progress = cheb(sx, sy, tx, ty) - nds
        # tie-break: prefer staying closer to opponent (slightly) to disrupt safe collector
        odo = cheb(nx, ny, ox, oy)
        lex = (dx, dy)
        score = (nds, -progress, odo)
        if score < best_score or (score == best_score and lex < (best_move[0], best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]