def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        dx = 0 if sx == ox else (1 if sx < ox else -1)
        dy = 0 if sy == oy else (1 if sy < oy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny): return [dx, dy]
        for a in moves:
            nx, ny = sx + a[0], sy + a[1]
            if valid(nx, ny): return [a[0], a[1]]
        return [0, 0]

    best = None
    best_adv = -10**18
    # Target the resource where we can be closer than the opponent (Chebyshev race)
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - md  # positive: we're closer
        # slight preference for nearer resources to avoid dithering
        tie = - (md + 0.01 * (rx + ry))
        score = adv * 1000 + tie
        if score > best_adv:
            best_adv = score
            best = (rx, ry)

    tx, ty = best
    cur_md = cheb(sx, sy, tx, ty)
    cur_od = cheb(ox, oy, tx, ty)

    # Choose move that improves our race, avoids obstacles, and pressures the target
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        md = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)  # opponent position unchanged this turn
        adv = od - md
        # Primary: increase advantage; Secondary: reduce distance to target; Tertiary: avoid letting opponent improve relative access
        improve = (cur_od - cur_md) - adv
        score = adv * 1000 + (cur_md - md) * 50 - improve * 10 - (md * 2)
        # If we're already on the resource, stay/move doesn't matter; favor staying
        if (sx, sy) == (tx, ty) and (dx, dy) == (0, 0):
            score += 10000
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]