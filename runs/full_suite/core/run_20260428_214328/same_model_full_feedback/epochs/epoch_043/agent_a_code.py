def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_r = None
    best_key = None
    # Pick the resource we can reach earlier with tie-breaking by "value" (closer to opponent after we take it)
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer ds significantly smaller than do; if equal, prefer smaller do (opponent not too close)
        key = (-(do - ds), ds, do, rx + ry, rx)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    # Choose move that improves our approach to chosen resource while pushing opponent away from it
    best_move = (0, 0)
    best_score = None
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inside(nx, ny):
            continue
        ds2 = cheb(nx, ny, rx, ry)
        do2 = cheb(ox, oy, rx, ry)
        # Small bias: prefer moves that also reduce distance to nearest other resource if we are tied
        near_other = None
        for ax, ay in resources:
            if (ax, ay) == (rx, ry):
                continue
            dso = cheb(nx, ny, ax, ay)
            if near_other is None or dso < near_other:
                near_other = dso
        near_other = near_other if near_other is not None else 0

        # Score: primarily minimize ds2 and maximize opponent separation via (do2 - ds2)
        sep = do2 - ds2
        score = (-sep, ds2, -near_other, dxm, dym)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]