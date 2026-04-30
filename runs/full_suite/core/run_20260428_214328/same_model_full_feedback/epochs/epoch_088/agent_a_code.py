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

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Select target resource with best relative advantage
    target = None
    best_rel = -10**18
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        rel = (d_op - d_me)  # positive means we are closer
        # Slight bias toward smaller own distance to finish sooner
        rel2 = rel * 100 - d_me
        if rel2 > best_rel:
            best_rel = rel2
            target = (rx, ry)

    if not resources:
        # No visible resources: maximize distance from opponent to reduce collision pressure
        best = None
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = cheb(nx, ny, ox, oy)
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    rx, ry = target

    # Evaluate moves: approach target, ensure opponent not too close, and prefer safer squares
    best = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_me = cheb(nx, ny, rx, ry)
        d_op = cheb(nx, ny, ox, oy)

        # If our move would let opponent reach target much sooner, penalize
        opp_to_target = cheb(ox, oy, rx, ry)

        # "Safety": count valid neighboring squares (deterministic local pressure)
        neigh = 0
        for ddx, ddy in dirs:
            tx, ty = nx + ddx, ny + ddy
            if ok(tx, ty):
                neigh += 1

        score = -d_me * 120 + d_op * 8 + neigh * 2 - (opp_to_target - d_me) * 30
        # Small deterministic tie-break: prefer staying or moving toward increasing x then y
        score += (nx - sx) * 0.001 + (ny - sy) * 0.0001

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]