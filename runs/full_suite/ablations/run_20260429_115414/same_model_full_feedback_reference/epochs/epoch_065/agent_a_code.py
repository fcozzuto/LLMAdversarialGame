def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
    if not resources:
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, int(round(cx)), int(round(cy)))
            score = -d
            if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
        return [best[1][0], best[1][1]]

    best_res = None
    best_adv = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # prefer resources we can reach sooner
        if best_res is None or adv > best_adv or (adv == best_adv and (ds < cheb(sx, sy, best_res[0], best_res[1]) or (ds == cheb(sx, sy, best_res[0], best_res[1]) and (rx, ry) < best_res))):
            best_adv = adv
            best_res = (rx, ry)

    rx, ry = best_res
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds = cheb(nx, ny, rx, ry)
        # slight tie-breaker toward center for stability
        center_bias = -cheb(nx, ny, int(round(cx)), int(round(cy)))
        # also consider opponent pressure on same resource
        do = cheb(ox, oy, rx, ry)
        score = (do - ds) * 10 - ds + center_bias
        if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))
    return [best[1][0], best[1][1]]