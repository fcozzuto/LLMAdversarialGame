def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in dirs:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    legal = [(dx, dy) for dx, dy in dirs if ok(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources, move to increase distance from opponent (stall deterministically).
    if not resources:
        best, bestv = legal[0], -10**9
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Target resources we are relatively closer to; otherwise deny opponent by moving away from their closest fronts.
    best, bestv = legal[0], -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Prefer not to step into immediate opponent reach.
        opp_reach = cheb(nx, ny, ox, oy)
        # Larger is better; compute advantage over opponent across all resources (max over targets).
        best_adv = -10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = (do - ds)  # positive means we are closer to this resource than opponent
            # Small tie-break: slightly prefer nearer resources for quicker scoring.
            adv -= 0.05 * ds
            if adv > best_adv:
                best_adv = adv
        v = best_adv * 1000 + opp_reach
        if v > bestv:
            bestv, best = v, (dx, dy)
    return [best[0], best[1]]