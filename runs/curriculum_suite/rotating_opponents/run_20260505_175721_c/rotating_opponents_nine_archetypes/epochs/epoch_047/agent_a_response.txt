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

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    # Precompute a small deterministic subset of resources near current midpoint to keep logic sharp
    mx, my = (sx + ox) // 2, (sy + oy) // 2
    res_sorted = sorted(resources, key=lambda t: abs(t[0] - mx) + abs(t[1] - my))
    consider = res_sorted[: min(6, len(res_sorted))]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate: choose the target resource where we gain most reach advantage,
        # plus a small penalty for moving too slowly (distance).
        my_best = None
        for tx, ty in consider:
            sd = abs(nx - tx) + abs(ny - ty)
            od = abs(ox - tx) + abs(oy - ty)
            gain = od - sd  # positive means we are closer than opponent
            val = (gain * 1000) - sd
            if my_best is None or val > my_best:
                my_best = val

        # Obstacle "pressure": prefer cells with more free adjacent space
        free_adj = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) not in obstacles:
                free_adj += 1

        # Also prevent drifting into opponent by slightly penalizing reducing opponent-target advantage too much
        # (still deterministic, based only on current position and considered resources).
        opp_pen = 0
        for tx, ty in consider:
            od = abs(ox - tx) + abs(oy - ty)
            myd = abs(nx - tx) + abs(ny - ty)
            if myd > od:
                opp_pen += 1

        key = (-(opp_pen), -(my_best), -free_adj, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]] if best else [0, 0]