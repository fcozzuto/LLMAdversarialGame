def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    remaining = observation.get("remaining_resource_count", len(resources))

    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dx = -dx if dx < 0 else dx
        dy = ay - by
        dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2

    if not resources or remaining <= 0:
        best = None; bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = -cheb(nx, ny, cx, cy) - 0.12 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [int(best[0]), int(best[1])]

    opp_close = cheb(sx, sy, ox, oy) <= 1
    # Score each move by contesting a resource: maximize (opp_dist - self_dist), with fallback to progress.
    best = None; bestv = -10**18
    for dx, dy, nx, ny in legal:
        # small preference to avoid stepping into obstacle-adjacent tiles (deterministic local safety)
        safety_pen = 0
        for ax, ay in ((nx-1, ny),(nx+1, ny),(nx, ny-1),(nx, ny+1)):
            if inb(ax, ay) and (ax, ay) in blocked:
                safety_pen += 1
        best_res = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # contest margin: positive means we are closer (or reduce their lead)
            margin = (od - sd)
            # prioritize nearer resources once margins are similar
            v = 2.2 * margin - 0.08 * sd
            if opp_close:
                # when adjacent, slightly prefer resources that are also close to opponent (we can "trade" turns)
                v += 0.15 * (2 - cheb(ox, oy, rx, ry))
            if v > best_res:
                best_res = v
        # Also slightly prefer moving toward the center and away from being too far from resources
        center_bias = -0.05 * cheb(nx, ny, cx, cy)
        far_pen = -0.01 * min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        total = best_res + center_bias + far_pen - 0.25 * safety_pen
        if total > bestv:
            bestv = total; best = (dx, dy)

    return [int(best[0]), int(best[1])]