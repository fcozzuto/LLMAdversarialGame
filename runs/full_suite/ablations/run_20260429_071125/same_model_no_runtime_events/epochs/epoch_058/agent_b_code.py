def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    if not resources:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    # Pick the resource that maximizes advantage (self closer than opponent).
    best = None
    best_adv = -10**9
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        adv = (do - ds) * 10 - ds  # strong preference to resources opponent is farther from
        if adv > best_adv:
            best_adv = adv
            best = (tx, ty)

    tx, ty = best
    best_move = (0, 0)
    best_score = -10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if not inb(sx + dx, sy + dy):
                continue
            nx, ny = sx + dx, sy + dy
            ds2 = cheb(nx, ny, tx, ty)
            # Also avoid moves that let opponent immediately get closer to the same target.
            do2 = cheb(ox, oy, tx, ty)
            score = -ds2 * 3 + (do2 - ds2)  # still primarily go to target
            if score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]