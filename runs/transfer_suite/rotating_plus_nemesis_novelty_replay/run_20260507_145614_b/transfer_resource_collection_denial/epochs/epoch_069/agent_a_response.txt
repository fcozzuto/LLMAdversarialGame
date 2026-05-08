def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        return [0 if sx == tx else (1 if tx > sx else -1), 0 if sy == ty else (1 if ty > sy else -1)]

    if any((sx == r[0] and sy == r[1]) for r in resources):
        return [0, 0]

    rem = observation.get("remaining_resource_count", len(resources))
    risk_weight = 1.0 + (16.0 / (1.0 + rem))  # later: less risk, earlier: more cautious

    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx = dy = 0

        # Choose the best resource from this next position using a "self-claim margin" heuristic
        # margin = (opp_dist - self_dist); prefer resources where we are already (or become) closer.
        cur_best = -10**18
        for rx, ry in resources:
            if rx == nx and ry == ny:
                return [dx, dy]
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            margin = do - ds
            # Extra term to avoid heading into "sure opponent" resources too early
            if margin >= 0:
                v = 1000.0 * margin - 1.0 * ds
            else:
                v = risk_weight * margin - 0.3 * ds  # still can steal late, but penalize now
            if v > cur_best:
                cur_best = v

        # Small nudge to reduce distance to the best-evaluated resource set (prevents dithering)
        # Also mildly bias away from opponent by preferring moves that increase opp distance to closest resource.
        opp_closest = 10**9
        self_closest = 10**9
        for rx, ry in resources:
            opp_closest = min(opp_closest, dist(ox, oy, rx, ry))
            self_closest = min(self_closest, dist(nx, ny, rx, ry))
        v2 = cur_best - 0.02 * max(0, self_closest - opp_closest)

        if v2 > bestv:
            bestv = v2
            best = (dx, dy)

    return [best[0], best[1]]