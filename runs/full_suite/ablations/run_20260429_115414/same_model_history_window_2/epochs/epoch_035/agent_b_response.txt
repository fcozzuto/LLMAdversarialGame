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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    inb = lambda x, y: 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    best_target = None
    best_val = -10**9
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        val = (do - ds) * 12 - ds
        if val > best_val:
            best_val, best_target = val, (rx, ry)

    # If no target, drift to center while keeping distance from opponent
    if best_target is None:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**9, (0, 0))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            score = -cheb(nx, ny, cx, cy) + 0.8 * cheb(nx, ny, ox, oy)
            if score > best[0]:
                best = (score, (dx, dy))
        return [int(best[1][0]), int(best[1][1])]

    rx, ry = best_target
    best = (-10**9, (0, 0))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds_next = cheb(nx, ny, rx, ry)
        do_now = cheb(ox, oy, rx, ry)
        opp_to_target = do_now - cheb(ox, oy, nx, ny)
        eat_bonus = 6 if (nx, ny) == (rx, ry) else 0
        # Main: get closer to our target; Secondary: reduce opponent's ability to race (maximize opponent delay)
        score = (-ds_next * 10) + (do_now * 2) + eat_bonus + 0.5 * (opp_to_target) - 0.25 * cheb(nx, ny, ox, oy)
        if score > best[0]:
            best = (score, (dx, dy))
    return [int(best[1][0]), int(best[1][1])]