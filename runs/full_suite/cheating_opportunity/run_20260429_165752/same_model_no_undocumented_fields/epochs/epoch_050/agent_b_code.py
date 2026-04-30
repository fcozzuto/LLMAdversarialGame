def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    s = observation.get("self_position", [0, 0])
    o = observation.get("opponent_position", [0, 0])
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    # If resources exist, pick the move that best balances:
    # - progress toward a resource
    # - denying opponent progress to that same resource
    # - avoiding getting too close to opponent
    if resources:
        best = None
        # Deterministic tie-break: fixed resource ordering by coordinates
        resources_sorted = sorted(resources, key=lambda r: (r[0], r[1]))
        for dx, dy, nx, ny in legal:
            my_best = 10**9
            opp_best = 10**9
            for rx, ry in resources_sorted:
                myd = cheb(nx, ny, rx, ry)
                oppd = cheb(ox, oy, rx, ry)
                if myd < my_best: my_best = myd
                if oppd < opp_best: opp_best = oppd
            # Score: lower is better
            # - strong preference to reduce my distance to nearest resource
            # - penalize when opponent is also close (can't be computed exactly for the moved resource, but use best)
            # - keep some distance from opponent
            myd_current = min(cheb(nx, ny, rx, ry) for rx, ry in resources_sorted)
            myd_after = myd_current
            oppd_near = min(cheb(ox, oy, rx, ry) for rx, ry in resources_sorted)
            dist_opp = cheb(nx, ny, ox, oy)
            score = (myd_after * 10) - (oppd_near * 4) - (dist_opp * 1)
            if best is None or score < best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
        return [best[1][0], best[1][1]]

    # No resources visible: move to safer square that also moves away from opponent cornering.
    best = None
    for dx, dy, nx, ny in legal:
        dist_opp = cheb(nx, ny, ox, oy)
        # Encourage advancing directionally (toward center) to avoid stagnation
        center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0
        center_dist = cheb(int(nx), int(ny), int(center_x), int(center_y))
        score = (-dist_opp * 5) + center_dist
        if best is None or score < best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))
    return [best[1][0], best[1][1]]