def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = 0 if sx < w // 2 else w - 1, 0 if sy < h // 2 else h - 1
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]] if best[0] != 10**9 else [0, 0]

    # Pick a resource where we have maximum advantage over the opponent in Chebyshev distance.
    best_r = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd  # prefer where opponent is farther
        key = (-adv, myd, cheb(sx, sy, rx, ry) + cheb(ox, oy, rx, ry))
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r

    # Greedy step towards target with obstacle handling and mild opponent-avoidance.
    best = (10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to = cheb(nx, ny, rx, ry)
        d_op = cheb(nx, ny, ox, oy)
        # If we can reduce target distance, strongly prefer it; otherwise, keep options open.
        score = d_to * 1000 - d_op
        if d_to == cheb(sx, sy, rx, ry) and (nx, ny) == (sx, sy):
            score += 50
        if score < best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]] if best[0] != 10**18 else [0, 0]