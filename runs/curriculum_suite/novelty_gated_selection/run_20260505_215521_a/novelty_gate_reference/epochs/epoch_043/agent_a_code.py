def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Score candidate moves by: go to best resource, avoid opponent when close, avoid obstacles already handled by free().
    best_move = [0, 0]
    best_val = -10**18
    res_list = resources[:]  # local deterministic copy

    # Precompute closest resource distances in a cheap way by direct evaluation of candidates.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Resource value: prefer collecting if adjacent/at, otherwise reduce distance; slight tie-break by resource ordering (stable).
        res_val = 0
        if res_list:
            md = 10**9
            mi = 0
            for i, (rx, ry) in enumerate(res_list):
                d = abs(nx - rx) + abs(ny - ry)
                if d < md:
                    md = d
                    mi = i
            rx, ry = res_list[mi]
            if md == 0:
                res_val = 10**6
            else:
                res_val = 2000 / (md + 1)  # deterministic float calc
                # gentle preference to move toward resources with smaller x when tied (deterministic bias)
                res_val += (w - rx) * 0.5 + (h - ry) * 0.1
        else:
            res_val = 0

        # Opponent avoidance: when close, increase penalty; also try to change relative alignment.
        dopt = abs(nx - ox) + abs(ny - oy)
        opp_pen = 0
        if dopt <= 2:
            opp_pen = 5000 / (dopt + 1)
        elif dopt <= 4:
            opp_pen = 1200 / (dopt + 1)

        # If opponent is adjacent, prioritize moving to maximize distance rather than resource.
        if dopt == 1:
            dist_boost = 10000 * (dopt)  # larger when dopt remains 1, but we already compute after move; use distance improvement instead:
            # stronger: maximize new distance (deterministic)
            dist_boost = 20000 * (abs((nx + (nx - ox))) + abs((ny + (ny - oy))))
            val = dist_boost - opp_pen + res_val
        else:
            val = res_val - opp_pen

        # Small deterministic nudge to reduce oscillation: prefer not to stay unless necessary.
        if dx == 0 and dy == 0:
            val -= 3

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move