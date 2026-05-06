def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obst = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    # Opponent's likely target: nearest resource to opponent (tie by stable ordering).
    opp_target = None
    best_rd = None
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if best_rd is None or d < best_rd:
            best_rd = d
            opp_target = (rx, ry)

    tx, ty = opp_target

    def step_toward(px, py, target):
        prx, pry = px, py
        tx, ty = target
        best = None
        bestd = None
        for dx, dy in deltas:
            nx, ny = prx + dx, pry + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obst:
                continue
            d = man(nx, ny, tx, ty)
            # tie-break deterministically: prefer smaller dx then dy (implicit by deltas order)
            if bestd is None or d < bestd:
                bestd = d
                best = (dx, dy)
        return best if best is not None else (0, 0)

    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0
    def center_bias(x, y):
        dx = x - cx0
        dy = y - cy0
        return -0.002 * (dx * dx + dy * dy)

    def resource_score_at(x, y):
        # Prefer states closer to some resource; also favor closeness to opponent's target to deny tempo.
        mind_all = 10**9
        for rx, ry in resources:
            if (rx, ry) in obst:
                continue
            d = man(x, y, rx, ry)
            if d < mind_all:
                mind_all = d
        d_to_target = man(x, y, tx, ty)
        return (-0.6 * d_to_target) + (-0.25 * mind_all)

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        odx, ody = step_toward(ox, oy, (tx, ty))
        nox, noy = ox + odx, oy + ody
        if (nox, noy) in obst or not inb(nox, noy):
            nox, noy = ox, oy

        our_d = man(nx, ny, tx, ty)
        opp_d = man(nox, noy, tx, ty)

        # Primary: gain against opponent at their likely target.
        # Secondary: deny by maximizing our advantage and getting closer to any resource.
        # Tertiary: center bias.
        val = (opp_d - our_d)
        val += 0.8 * (resource_score_at(nx, ny) - resource_score_at(sx, sy))
        val += center_bias(nx, ny)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]