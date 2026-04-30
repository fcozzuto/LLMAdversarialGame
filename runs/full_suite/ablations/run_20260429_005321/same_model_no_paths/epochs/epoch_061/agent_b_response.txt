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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obst(x, y):
        pen = 0
        for ddx in (-1, 0, 1):
            nx = x + ddx
            if nx < 0 or nx >= w: 
                continue
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ny = y + ddy
                if 0 <= ny < h and (nx, ny) in obstacles:
                    pen += 1
        return pen

    if not resources:
        return [0, 0]

    best = None
    best_score = -10**9
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we are relatively closer; also avoid resource near obstacles.
        score = (do - ds) - (2 * near_obst(rx, ry)) - (1 if (rx, ry) in obstacles else 0)
        if score > best_score or (score == best_score and (rx + ry) < (best[0] + best[1])):
            best_score = score
            best = (rx, ry)

    tx, ty = best

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-breaking: prefer diagonal, then cardinal, then stay.
    pref = {(dx, dy): i for i, (dx, dy) in enumerate(moves)}

    curd = cheb(sx, sy, tx, ty)
    best_m = (0, 0)
    best_v = -10**9
    best_pref = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        progress = curd - nd
        v = progress * 10 - nd - near_obst(nx, ny)
        if v > best_v or (v == best_v and pref[(dx, dy)] < best_pref):
            best_v = v
            best_pref = pref[(dx, dy)]
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]