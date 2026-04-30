def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        # Move to keep pressure away from opponent, toward center
        cx, cy = w // 2, h // 2
        best = (0, 0)
        bestv = -10**18
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                    v = (abs(nx - cx) + abs(ny - cy)) * -1 + (max(abs(nx - ox), abs(ny - oy)))
                    if v > bestv:
                        bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    my_pos = (sx, sy)
    op_pos = (ox, oy)

    # Choose target resource that we are best positioned to contest/intercept (minimize myd-opd).
    best_target = None
    best_margin = 10**18
    for r in resources:
        md = cheb(my_pos, r)
        od = cheb(op_pos, r)
        margin = md - od
        if margin < best_margin:
            best_margin = margin
            best_target = r

    tx, ty = best_target

    # Evaluate next moves with a deterministic heuristic.
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        my2 = (nx, ny)

        # Core: get closer to target; maintain advantage vs opponent at that target.
        d_my = cheb(my2, (tx, ty))
        d_op = cheb(op_pos, (tx, ty))
        contest_adv = (d_op - d_my)  # higher is better (we become closer than opponent)
        # Secondary: encourage distancing from opponent unless it worsens contest.
        dist_op_now = cheb(my2, op_pos)

        # If we move onto a resource, strongly favor.
        on_resource = 1 if (nx, ny) in resources else 0

        v = 0
        v += on_resource * 10**6
        v += contest_adv * 2000
        v += (-d_my) * 50
        v += dist_op_now * 2

        # Mild obstacle-aware bias via edge of map (avoid corners too hard if not needed)
        v += -(abs(nx - w // 2) + abs(ny - h // 2)) * 0.2

        if v > bestv:
            bestv, best = v, (dx, dy)

    return [best[0], best[1]]