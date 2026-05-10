def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obstacle_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = bx - ax
        dy = by - ay
        return (dx if dx >= 0 else -dx) if (abs(dx) > abs(dy)) else (dy if dy >= 0 else -dy)

    def step_pos(pos, mv):
        x, y = pos
        dx, dy = mv
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacle_set:
            return x, y
        return nx, ny

    def best_target_for_us():
        if not resources:
            return None
        best = None
        for r in resources:
            myd = cheb((sx, sy), r)
            od = cheb((ox, oy), r)
            # Prioritize resources where we're closer (or can swing quickly).
            key = (-(od - myd), myd, r[0], r[1])
            if best is None or key < best[0]:
                best = (key, r)
        return best[1]

    target = best_target_for_us()
    if target is None:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Assume opponent also greedily heads to its nearest resource each turn.
    opp_target = None
    if resources:
        besto = None
        for r in resources:
            od = cheb((ox, oy), r)
            key = (od, r[0], r[1])
            if besto is None or key < besto[0]:
                besto = (key, r)
        opp_target = besto[1] if besto else None

    def opp_next_pos():
        if opp_target is None:
            return ox, oy
        # Choose move that minimizes distance to opp_target.
        bestm = (10**9, 10**9, 0, 0)
        bestp = (ox, oy)
        for mv in moves:
            nx, ny = step_pos((ox, oy), mv)
            d = cheb((nx, ny), opp_target)
            key = (d, abs(mv[0]) + abs(mv[1]), mv[0], mv[1])
            if key < bestm:
                bestm = key
                bestp = (nx, ny)
        return bestp

    nox, noy = opp_next_pos()

    best_move = (10**9, 10**9, 10**9, 0, 0)
    for mv in moves:
        nx, ny = step_pos((sx, sy), mv)
        myd = cheb((nx, ny), target)
        od = cheb((nox, noy), target)  # estimated opponent distance next
        # Want to be closer than opponent; also prefer collecting quickly (smaller myd).
        key = (-(od - myd), myd, (nx - sx) * (nx - sx) + (ny - sy) * (ny - sy), mv[0], mv[1])
        if key < best_move:
            best_move = key

    return [int(best_move[3]), int(best_move[4])]