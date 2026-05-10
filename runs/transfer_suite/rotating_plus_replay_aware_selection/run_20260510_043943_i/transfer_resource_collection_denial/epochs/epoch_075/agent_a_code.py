def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break: prefer larger dx then dy, then stay.
    deltas_sorted = sorted(deltas, key=lambda d: (-(d[0] != 0), -abs(d[0]), -abs(d[1]), -d[0], -d[1]))

    best_score = None
    best_move = [0, 0]

    # Prefer moves that: (1) make us earlier to some resource, (2) reduce opponent advantage,
    # (3) avoid stepping into obstacle-adjacent traps when possible.
    def trap_penalty(x, y):
        p = 0
        # if we are adjacent to an obstacle, being there is riskier (opponent sweepers exploit paths)
        for ax, ay in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)):
            nx, ny = x + ax, y + ay
            if (nx, ny) in obstacles:
                p += 1
        return p

    for dx, dy in deltas_sorted:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy

        # Evaluate: choose the resource that maximizes our win margin after this move.
        best_for_move = None
        for rx, ry in resources:
            if not ok(rx, ry):
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            # Add small preference for closer targets even if margin is similar.
            margin = od - sd  # positive => we arrive earlier
            near = -(sd + (0.2 * trap_penalty(nx, ny)))
            # Encourage threatening resources where opponent is relatively far.
            value = margin * 10 + near

            if best_for_move is None or value > best_for_move:
                best_for_move = value

        # If all resources are invalid, just move safely toward center.
        if best_for_move is None:
            cx, cy = w // 2, h // 2
            sd = man(nx, ny, cx, cy)
            od = man(ox, oy, cx, cy)
            best_for_move = (od - sd) * 5 - sd

        if best_score is None or best_for_move > best_score:
            best_score = best_for_move
            best_move = [nx - sx, ny - sy]

    # Final safety: ensure returned move delta is in {-1,0,1}
    mdx, mdy = best_move[0], best_move[1]
    if mdx > 1:
        mdx = 1
    if mdx < -1:
        mdx = -1
    if mdy > 1:
        mdy = 1
    if mdy < -1:
        mdy = -1
    return [int(mdx), int(mdy)]