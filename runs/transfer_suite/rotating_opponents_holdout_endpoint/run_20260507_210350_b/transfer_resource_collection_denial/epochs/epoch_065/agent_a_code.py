def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    best_score = None
    tx = ty = resources[0][0]
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = (do - ds, -ds, -(rx * 31 + ry))
        if best_score is None or score > best_score:
            best_score = score
            tx, ty = rx, ry

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    # Prefer moves that reduce our distance to target; break ties by advantage over opponent, then lexicographic.
    best = None
    for dx, dy, nx, ny in cand:
        ns = cheb(nx, ny, tx, ty)
        ns0 = cheb(sx, sy, tx, ty)
        no = cheb(ox, oy, tx, ty)
        score = (no - ns, -ns, -abs(tx - nx) - abs(ty - ny), dx, dy)
        # Small preference to actually progress if already at target.
        if ns == 0 and ns0 == 0:
            score = (score[0], score[1], score[2], dx + 10, dy + 10)
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]