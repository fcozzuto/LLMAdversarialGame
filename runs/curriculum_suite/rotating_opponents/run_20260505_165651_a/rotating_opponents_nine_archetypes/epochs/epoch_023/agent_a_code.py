def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # deterministic: move towards opponent to contest tempo
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if inb(nx, ny) else [0, 0]

    # Corner_guard often anchors; counter by aiming to become strictly closer than opponent
    # on a high-value resource, otherwise transition toward the most contestable one.
    center = ((w - 1) / 2.0, (h - 1) / 2.0)
    best = None

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny):
            continue

        # For each resource compute "beat margin" = oppd - myd (positive means I am closer)
        my_best_my = 10**9
        my_best_beat = -10**9
        my_tight = 10**9  # distance to most reachable-by-contest resource
        for rx, ry in resources:
            myd = king_dist(nx, ny, rx, ry)
            oppd = king_dist(ox, oy, rx, ry)
            beat = oppd - myd
            if beat > my_best_beat or (beat == my_best_beat and myd < my_best_my):
                my_best_beat = beat
                my_best_my = myd
            if oppd <= myd + 1 and myd < my_tight:
                my_tight = myd

        # Tie-breaking favors:
        # 1) positive beat (strict advantage) then 2) larger beat then 3) smaller my distance
        # 4) slightly prefer moving toward board center to escape corner-anchoring
        cx, cy = center
        center_bias = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        stay_pen = 1 if (dxm == 0 and dym == 0) else 0

        key = (my_best_beat, -my_best_my, my_tight if my_tight < 10**8 else 10**8, center_bias, -stay_pen, dxm, dym)
        if best is None or key > best[0]:
            best = (key, [dxm, dym])

    return best[1] if best is not None else [0, 0]