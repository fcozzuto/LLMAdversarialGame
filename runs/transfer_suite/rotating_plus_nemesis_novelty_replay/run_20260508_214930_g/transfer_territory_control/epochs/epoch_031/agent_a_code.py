def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def neighbors(nx, ny):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    ax, ay = nx + dx, ny + dy
                    if 0 <= ax < w and 0 <= ay < h:
                        yield ax, ay

    def count_adj(nx, ny, sset):
        c = 0
        for ax, ay in neighbors(nx, ny):
            if (ax, ay) in sset:
                c += 1
        return c

    def eval_cell(nx, ny):
        if not inside(nx, ny):
            return -10**9
        in_self = (nx, ny) in self_t
        in_opp = (nx, ny) in opp_t
        in_un = (nx, ny) in unclaimed

        d_center = abs(nx - cx) + abs(ny - cy)
        gain = 0
        if in_un:
            gain += 7
        elif in_self:
            gain += 2
        elif in_opp:
            gain += 4 + 2 * count_adj(nx, ny, self_t) - 1 * count_adj(nx, ny, opp_t)
        adj_self = count_adj(nx, ny, self_t)
        adj_opp = count_adj(nx, ny, opp_t)

        # Prefer moves that expand while reducing exposure to opponent-held mass
        risk = 0
        if in_opp:
            risk += max(0, adj_opp - adj_self)
        else:
            risk += max(0, adj_opp - 2)

        # Deterministic center contest pressure
        return 20 - d_center * 2 + gain + adj_self - risk

    best = (-10**18, (0, 0))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = eval_cell(nx, ny)
        if sc > best[0] or (sc == best[0] and (dx, dy) < best[1]):
            best = (sc, (dx, dy))
    return [best[1][0], best[1][1]]