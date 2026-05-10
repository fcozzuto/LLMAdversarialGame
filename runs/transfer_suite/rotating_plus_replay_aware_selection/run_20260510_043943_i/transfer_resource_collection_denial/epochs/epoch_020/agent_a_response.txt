def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cell_blocked(x, y):
        return (x, y) in obstacles

    if not resources:
        # deterministic evade: move to maximize min distance to any adjacent opponent step
        best = (0, 0)
        best_sc = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or cell_blocked(nx, ny):
                continue
            # consider opponent possible next position as its direct move
            min_d = 10**9
            for odx, ody in deltas:
                tx, ty = ox + odx, oy + ody
                if inb(tx, ty) and not cell_blocked(tx, ty):
                    d = man(nx, ny, tx, ty)
                    if d < min_d:
                        min_d = d
            sc = (min_d, -man(nx, ny, ox, oy))
            if best_sc is None or sc > best_sc:
                best_sc = sc
                best = (dx, dy)
        return [best[0], best[1]]

    # pick a target resource where we are relatively better placed (opponent not closest)
    best_target = None
    best_tsc = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources opponent can't reach much faster; tie-break favors closeness for us.
        tsc = (do - ds, -ds)
        if best_tsc is None or tsc > best_tsc:
            best_tsc = tsc
            best_target = (rx, ry)

    tx, ty = best_target
    # evaluate immediate move: minimize distance to target while not stepping into opponent denier zone
    best = (0, 0)
    best_sc = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or cell_blocked(nx, ny):
            continue
        self_d = man(nx, ny, tx, ty)

        # estimate opponent reachability to our target after one step
        opp_best_d = 10**9
        for odx, ody in deltas:
            ax, ay = ox + odx, oy + ody
            if inb(ax, ay) and not cell_blocked(ax, ay):
                d = man(ax, ay, tx, ty)
                if d < opp_best_d:
                    opp_best_d = d

        # If opponent can get closer than us, penalize; otherwise reward.
        competition = opp_best_d - self_d
        # slight bias toward reducing opponent distance too (resource denial archetype)
        sc = (competition, -self_d, -man(nx, ny, ox, oy), dx, dy)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [best[0], best[1]]