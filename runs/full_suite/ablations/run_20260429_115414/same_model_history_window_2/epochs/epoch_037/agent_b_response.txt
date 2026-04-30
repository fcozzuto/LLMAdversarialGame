def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy) * 2 - cheb(nx, ny, sx, sy)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Target selection: prefer resources we are at least as close to as opponent; otherwise block it.
    best_t = resources[0]
    best_score = -10**18
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # If we can reach not later than opponent, heavily favor; else favor longer opponent access (potential denial).
        score = (do - ds) * 100 - ds
        # Mild tie-break toward resources closer to center to reduce path dead-ends.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= (abs(tx - cx) + abs(ty - cy)) * 0.1
        if score > best_score:
            best_score, best_t = score, (tx, ty)

    tx, ty = best_t

    # Move selection: reduce distance to target; if opponent threatens (is close), also reduce distance to opponent.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds_next = cheb(nx, ny, tx, ty)
        do_next = cheb(nx, ny, ox, oy)
        # If opponent is close to target too, try to create distance from opponent to avoid contest losses.
        do_t = cheb(ox, oy, tx, ty)
        ds_t = cheb(sx, sy, tx, ty)
        contest = 1 if do_t <= ds_t else 0
        v = -ds_next * 10 + do_next * (2 if contest else 0.5)
        # Small preference to move closer to opponent when we are clearly winning the target race.
        if do_t - ds_t >= 2:
            v += -do_next
        if v > bestv:
            bestv, best = v, (dx, dy)

    return [best[0], best[1]]