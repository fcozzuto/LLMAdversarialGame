def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # pick a target where we can "win" collection race; also prefer being closer
    best = None  # (key..., tx,ty)
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - sd  # positive => we are closer
        # secondary: how isolated it is (prefer resources with no close alternatives for opponent)
        m2 = 10**9
        for ux, uy in resources:
            if (ux, uy) != (tx, ty):
                d = cheb(ox, oy, ux, uy)
                if d < m2:
                    m2 = d
        if m2 == 10**9:
            m2 = od
        key = (-(adv), sd, m2, tx, ty)
        if best is None or key < best[0]:
            best = (key, tx, ty)

    _, tx, ty = best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        sd2 = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv2 = od - sd2
        # prefer not to give opponent an easier race on that same target
        opp_dist_to_target_after = od
        # also slight preference to move toward the target in manhattan-ish tie-break
        man = abs(nx - tx) + abs(ny - ty)
        key = (-adv2, sd2, opp_dist_to_target_after, man, tx, ty, dx, dy)
        if best_m is None or key < best_m[0]:
            best_m = (key, dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[1]), int(best_m[2])]