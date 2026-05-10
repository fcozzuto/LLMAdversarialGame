def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    op_list = list(opT)[:]
    un_list = list(unT)[:]
    op_list.sort(key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    un_list.sort(key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))

    # Prefer direct flipping on entry; if none, expand toward unclaimed.
    targets = op_list[:6] if op_list else []
    if not targets and un_list:
        targets = un_list[:6]

    best = [0, 0]
    bestv = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            continue
        # Proxy: prefer opponent cell entry; else unclaimed. Add frontier pressure.
        v = 0.0
        center = -0.15 * ((nx - cx) ** 2 + (ny - cy) ** 2)  # gentle central bias
        v += center

        if (nx, ny) in opT:
            v += 50.0
        if (nx, ny) in unT:
            v += 8.0

        # Frontier control: moving to neighbor of opponent territory increases flip chances.
        adj_op = 0
        for ddx, ddy in dirs:
            ax, ay = nx + ddx, ny + ddy
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in opT:
                adj_op += 1
        v += 2.0 * adj_op

        # Distance to best target(s)
        if targets:
            dmin = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
            v += -2.0 * dmin

        # Avoid getting stuck in your own dense area: prefer expanding outward
        neigh_self = 0
        for ddx, ddy in dirs:
            ax, ay = nx + ddx, ny + ddy
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in selfT:
                neigh_self += 1
        v += -0.25 * neigh_self

        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = v
            best = [dx, dy]

    # If all moves were invalid (unlikely), stay.
    return [int(best[0]), int(best[1])]