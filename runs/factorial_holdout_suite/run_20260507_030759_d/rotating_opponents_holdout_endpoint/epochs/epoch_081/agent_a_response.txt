def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist(a, b):
        x1, y1 = a
        x2, y2 = b
        d = x1 - x2
        if d < 0: d = -d
        e = y1 - y2
        if e < 0: e = -e
        return d + e

    best = None
    best_sc = None
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)] + [(0, 0)]
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    res_cells = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                res_cells.append((x, y))
    if not res_cells:
        return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_pos = (nx, ny)

        my_d = 10**9
        opp_d_for_my = 10**9
        opp_d_best = 10**9

        for r in res_cells:
            d_my = dist(my_pos, r)
            if d_my < my_d:
                my_d = d_my
                opp_d_for_my = dist((ox, oy), r)
            d_opp = dist((ox, oy), r)
            if d_opp < opp_d_best:
                opp_d_best = d_opp

        # Prefer: getting closer to a resource that opponent is also near (race),
        # while still preventing opponent's closest resource advantage.
        # Small preference for advancing towards "front" (towards opponent corner) deterministically.
        front = (w - 1 - nx) + (h - 1 - ny)
        opp_front = (w - 1 - ox) + (h - 1 - oy)

        sc = (opp_d_for_my - my_d) * 100 - my_d * 2 + (opp_d_best - my_d) - (front - opp_front) * 0.01
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]