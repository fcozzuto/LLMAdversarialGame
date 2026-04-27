def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x, y, r):
        return abs(x - r[0]) + abs(y - r[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # Run to farthest corner-ish while avoiding obstacles
        tx, ty = (w - 1, h - 1) if sx + sy < (w - 1) + (h - 1) - (ox + oy) else (0, 0)
        best = (10**9, None)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            score = -(abs(nx - tx) + abs(ny - ty)) + 0.1 * (abs(nx - ox) + abs(ny - oy))
            if score > best[0]:
                best = (score, (dx, dy))
        return list(best[1] or [0, 0])

    # Choose a resource we are not worse-positioned to reach than opponent
    candidates = []
    for r in resources:
        d1 = md(sx, sy, r)
        d2 = md(ox, oy, r)
        # Prefer being closer; if tied, prefer higher "progress" direction and tie-break by coordinates
        gain = d2 - d1
        turn_bias = (r[0] + r[1])  # deterministic stable tie-break
        candidates.append((-(gain), d1, -turn_bias, r))
    candidates.sort()
    target = None
    # If all are worse, still take the nearest; otherwise pick best with positive gain
    for _, d1, _, r in candidates:
        if md(ox, oy, r) >= d1:
            target = r
            break
    if target is None:
        target = candidates[0][3]

    tx, ty = target
    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Reward approaching target, penalize getting closer to opponent when they threaten target area
        approach = - (abs(nx - tx) + abs(ny - ty))
        opp_dist = abs(nx - ox) + abs(ny - oy)

        # If opponent is also close to target, slightly prioritize denying their route by increasing distance
        opp_to_target = abs(ox - tx) + abs(oy - ty)
        opp_weight = 0.35 if opp_to_target <= (abs(sx - tx) + abs(sy - ty)) else 0.15
        val = approach + opp_weight * opp_dist

        # Tiny deterministic tie-break to avoid dithering on equal values
        val += 1e-6 * ((nx + 2*ny) % 7)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]