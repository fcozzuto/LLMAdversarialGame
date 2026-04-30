def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    cx, cy = (w - 1) // 2, (h - 1) // 2
    if not resources:
        best = None
        bestv = -10**18
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            # deterministic: go toward center but away from opponent slightly
            v = -cheb(nx, ny, cx, cy) + 0.3 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    best = None
    bestv = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Choose a target resource that we can reach competitively.
        # For each resource, prefer those where our distance advantage is largest.
        best_adv = -10**18
        best_rd = 10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive means we're closer than opponent would be
            if adv > best_adv or (adv == best_adv and sd < best_rd):
                best_adv = adv
                best_rd = sd
        # Overall: maximize advantage, then minimize our distance, then maximize distance from opponent.
        # Add tiny deterministic tie-break based on coordinate sum.
        oppd = cheb(nx, ny, ox, oy)
        tile = -((nx + ny) & 1) * 0.01
        v = 10.0 * best_adv - 1.0 * best_rd + 0.05 * oppd + tile
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]