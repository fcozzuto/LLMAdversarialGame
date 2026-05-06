def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev for diagonal movement

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (None, None, -10**9)

    # Prefer: secure a resource where we arrive not later than opponent; otherwise move to reduce opponent advantage.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        best_res_val = -10**9
        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            # arrive earlier matters most; discourage giving opponent a big lead
            lead = do - ds  # positive if we are closer or tie
            # small preference for overall closeness when contested similarly
            val = (lead * 10) - (ds * 1) + (rx + ry) * 0.0
            # if we can contest tightly, slightly prefer the resource that is nearer to us
            if lead >= 0:
                val += 2
            best_res_val = val if val > best_res_val else best_res_val

        # Secondary: avoid moving away from the "best contested direction"
        # Compute opponent-target pressure: how much we reduce their closest resource lead by moving.
        opp_pressure = 0
        # pick opponent's closest resource (with tie-break toward smaller coords deterministically)
        min_do = None
        best_opp_r = None
        for rx, ry in resources:
            do = dist(ox, oy, rx, ry)
            if min_do is None or do < min_do or (do == min_do and (rx, ry) < best_opp_r):
                min_do = do
                best_opp_r = (rx, ry)
        rx, ry = best_opp_r
        opp_pressure = (dist(ox, oy, rx, ry) - dist(nx, ny, rx, ry)) * 1.0  # positive if we get closer than opp to their target

        total = best_res_val + opp_pressure * 0.5
        if total > best[2]:
            best = (dx, dy, total)

    return [int(best[0]), int(best[1])]