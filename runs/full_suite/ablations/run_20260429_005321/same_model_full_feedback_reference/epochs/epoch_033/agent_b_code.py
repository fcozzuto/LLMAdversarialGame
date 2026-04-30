def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no resources remain, maximize distance from opponent.
    if not resources:
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                v = cheb(nx, ny, ox, oy)
                if bestv is None or v > bestv:
                    bestv = v
                    best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Pick a resource we can contest (or deny): minimize (our dist) while penalizing resources closer to opponent.
    best_r = None
    best_s = None
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # Competitive score: prefer resources we can reach sooner, but also consider denial when opponent is closer.
        s = d_self - 0.6 * d_opp
        if best_s is None or s < best_s:
            best_s = s
            best_r = (rx, ry)

    rx, ry = best_r
    best_move = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_to_target = cheb(nx, ny, rx, ry)
        d_opp = cheb(nx, ny, ox, oy)
        # If tie on reaching target, increase separation from opponent deterministically.
        val = (d_to_target, -d_opp, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]