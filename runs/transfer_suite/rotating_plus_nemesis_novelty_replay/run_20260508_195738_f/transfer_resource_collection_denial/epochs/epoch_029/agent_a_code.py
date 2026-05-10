def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)

    dxdy_moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            v = man(ox, oy, cx, cy) - 0.01 * man(sx, sy, cx, cy)
            if best is None or v > best[0]:
                best = (v, cx, cy)
        tx, ty = best[1], best[2]
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [int(dx), int(dy)]

    res = [(int(r[0]), int(r[1])) for r in resources]
    best_move = (0, 0)
    best_val = None

    # Deterministic ordering to keep ties stable
    for mdx, mdy in dxdy_moves:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue

        # Evaluate how advantaged we are to capture resources from the next cell
        best_delta = -10**9
        best_self = 10**9
        best_opp = 10**9
        for rx, ry in res:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            d = od - sd  # higher is better (we're closer than opponent)
            if d > best_delta or (d == best_delta and (sd < best_self or (sd == best_self and od < best_opp))):
                best_delta = d
                best_self = sd
                best_opp = od

        # Extra incentive: reduce our distance to the currently most favorable resource;
        # small penalty if opponent is extremely close there (likely race)
        v = best_delta * 1000 - best_self + (best_opp - best_self) * 0.05
        if best_val is None or v > best_val:
            best_val = v
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]