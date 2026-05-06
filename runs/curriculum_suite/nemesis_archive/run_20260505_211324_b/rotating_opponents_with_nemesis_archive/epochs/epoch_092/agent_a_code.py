def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_time(from_xy):
        if not res:
            return 10**9, None
        bestt = 10**9
        bestr = None
        for r in res:
            t = man(from_xy, r)
            if t < bestt:
                bestt, bestr = t, r
        return bestt, bestr

    my_best0, my_r0 = best_time((sx, sy))
    opp_best0, opp_r0 = best_time((ox, oy))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        my_t, my_r = best_time((nx, ny))

        # "Nemesis" pressure: choose cells that reduce opponent's closest resource time more than ours.
        opp_t, _ = best_time((ox, oy))

        # Estimate opponent's potential gain by how close our move gets to the resource we would take next.
        # If resources are tied, also prefer moving toward cells that are relatively farther from opponent.
        if res:
            # compute our advantage over the best opponent resource (static opponent time)
            # use target-based evaluation with small tie-breaks
            target = my_r if my_r is not None else my_r0
            adv = 0
            if target is not None:
                adv = (opp_best0 - my_t)
                # small bias: if we are about to take something that opponent also targets soon, fight it
                if opp_r0 is not None and target == opp_r0:
                    adv += 0.5
                # and if the chosen resource is "closer" to opponent than ours, punish
                if opp_best0 < my_t:
                    adv -= 0.3 * (my_t - opp_best0)

            # also incorporate our improvement from current
            val = (adv) - 0.15 * (my_t) + 0.05 * (opp_best0 - opp_t)
        else:
            val = -man((nx, ny), (w - 1, h - 1))

        # deterministic tie-break: prefer staying closer to center slightly (and lower dx,dy hash)
        if best is None or val > best[0]:
            best = (val, dx, dy)
        elif val == best[0]:
            cx, cy = w // 2, h // 2
            curd = abs(nx - cx) + abs(ny - cy)
            bestd = abs(sx + best[1] - cx) + abs(sy + best[2] - cy)
            if curd < bestd or (curd == bestd and (dx, dy) < (best[1], best[2])):
                best = (val, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]