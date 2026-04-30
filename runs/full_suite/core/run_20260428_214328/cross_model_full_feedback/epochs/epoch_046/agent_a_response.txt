def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    res_left = int(observation.get("remaining_resource_count", len(resources)) or len(resources))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue

        # Prefer positions that can "arrive" sooner than opponent to some resource.
        if resources:
            my_min = 10**9
            opp_min = 10**9
            for rx, ry in resources:
                md = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                if md < my_min: my_min = md
                if od < opp_min: opp_min = od
            # If resources are scarce, weight relative race more.
            rel = my_min - (0.9 + (0.15 if res_left <= 6 else 0.0)) * opp_min
            # Also lightly push to reduce absolute distance when rel ties.
            val = (rel, my_min)
        else:
            # No visible resources: drift toward center to increase future access.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            val = (cheb(nx, ny, cx, cy), cheb(nx, ny, ox, oy))

        # Obstacle adjacency penalty (avoid getting stuck in tight corners).
        adj = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0: 
                    continue
                ax2, ay2 = nx + adx, ny + ady
                if (ax2, ay2) in obst:
                    adj += 1
        val = (val[0] + adj * 0.3, val[1] + adj * 0.05)

        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]