def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        # Fallback: move toward a corner away from opponent
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy)) - (abs(c[0] - sx) + abs(c[1] - sy)))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        my_next = (nx, ny)

        # Pick the "most winnable" resource: prioritize where we are closer than opponent,
        # and otherwise choose a resource that minimizes how much we are behind.
        local_best = None
        local_val = None
        for rx, ry in resources:
            myd = cheb(my_next, (rx, ry))
            opd = cheb((ox, oy), (rx, ry))
            # Margin: positive means we arrive earlier; incorporate urgency and tie-break
            margin = opd - myd
            val = margin * 1000 - myd * 3 + (opd - myd) * (1 if myd == 0 else 0)
            if local_val is None or val > local_val or (val == local_val and (rx, ry) < local_best):
                local_val = val
                local_best = (rx, ry)

        # Small preference to not drift away from best resource direction
        opp_center = (ox, oy)
        steer = -cheb(my_next, opp_center) * 0.01
        val2 = local_val + steer

        if best_val is None or val2 > best_val or (val2 == best_val and (dx, dy) < tuple(best)):
            best_val = val2
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]