def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in dirs if free(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    # Target resources we can beat: maximize (opp_dist - self_dist), then minimize self_dist.
    best = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = (do - ds, -ds, rx, ry)
        if best is None or score > best[0]:
            best = (score, (rx, ry))

    def move_value(dx, dy, target):
        nx, ny = sx + dx, sy + dy
        if target is None:
            # Fallback: move to center while keeping distance from opponent
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dc = abs(nx - cx) + abs(ny - cy)
            dO = cheb(nx, ny, ox, oy)
            return (-dc, dO)
        tx, ty = target
        ds_new = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer moves that increase our lead and reduce distance to target
        lead = do - ds_new
        dOpp = cheb(nx, ny, ox, oy)
        return (lead, -ds_new, dOpp)

    # Deterministic choice by lexicographic ordering of move values.
    target = best[1] if best else None
    best_move = None
    for dx, dy in legal:
        v = move_value(dx, dy, target)
        if best_move is None or v > best_move[0]:
            best_move = (v, (dx, dy))
    return [int(best_move[1][0]), int(best_move[1][1])]