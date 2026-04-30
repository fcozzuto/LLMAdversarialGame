def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = {tuple(p) for p in obstacles}
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best_s = -10**9
        best_m = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                nx, ny = sx, sy
            d = man((nx, ny), (ox, oy))
            # deterministic slight center preference
            c = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
            s = d * 10 - c
            if s > best_s:
                best_s, best_m = s, (dx, dy)
        return [best_m[0], best_m[1]]

    res_list = [tuple(p) for p in resources]
    us = (sx, sy)
    op = (ox, oy)

    # Pick a target resource deterministically: prefer min our dist, tie by lexicographic
    best_t = None
    best_td = 10**9
    for r in res_list:
        d = man(us, r)
        if d < best_td or (d == best_td and r < best_t):
            best_td, best_t = d, r
    target = best_t

    # If opponent is closer to that target, we still move toward it but prioritize contesting
    dop = man(op, target)

    best_s = -10**18
    best_m = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            nx, ny = sx, sy
        pos = (nx, ny)

        dres = man(pos, target)
        on_res = 1 if pos in resources else 0

        d_op = man(pos, op)

        # contest logic: if opponent is closer to target, reduce their lead (increase separation from opponent
        # and pull toward target)
        lead = dop - man(us, target)
        contest = 1 if dop <= man(us, target) else 0

        # score: prioritize reducing distance to target, collecting, and keeping away when contested
        s = 0
        s += on_res * 10**7
        s += (10**4) * (-dres)
        s += (200 if contest else 60) * d_op
        s += (-5) * (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        # deterministic tie-break by move order and lexicographic position
        s += 0.001 * (-(dx * 3 + dy))

        if s > best_s:
            best_s, best_m = s, (dx, dy)

    return [best_m[0], best_m[1]]