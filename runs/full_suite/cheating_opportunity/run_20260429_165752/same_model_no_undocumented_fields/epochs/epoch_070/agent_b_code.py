def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If somehow on obstacle, step out deterministically
    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    # No resources: deterministically drift toward open area (maximize free neighbors)
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            cnt = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if free(tx, ty):
                    cnt += 1
            cand = (cnt, nx, ny)
            if best is None or cand > best:
                best = cand
        return [best[1] - sx, best[2] - sy] if best else [0, 0]

    # Choose target that is relatively worse for opponent (and closer for us)
    target = None
    best_t = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer: opponent farther, then us closer, then tie-break by coordinates
        cand = ((do - ds), (-ds), -rx, -ry)
        if best_t is None or cand > best_t:
            best_t = cand
            target = (rx, ry)

    rx, ry = target

    # Pick move that improves our progress to target while discouraging positions closer to opponent target race
    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        ds1 = cheb(nx, ny, rx, ry)
        do1 = cheb(ox, oy, rx, ry)
        # Heuristic: minimize our distance; also slightly prefer moves that keep opponent less able to contest (via our relative advantage)
        rel_adv = (do1 - ds1)
        cand = (ds1, -rel_adv, abs(nx - ox), nx, ny)
        if best_m is None or cand < best_m:
            best_m = cand
    if best_m is None:
        return [0, 0]
    nx, ny = best_m[3], best_m[4]
    return [nx - sx, ny - sy]