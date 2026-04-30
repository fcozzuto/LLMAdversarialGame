def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    def valid(nx, ny):
        return in_bounds(nx, ny) and (nx, ny) not in obstacles

    if resources:
        tx, ty = min(resources, key=lambda r: (cheb(ox, oy, r[0], r[1]), r[0], r[1]))
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # primary: maximize lead (opp distance - my distance)
            # secondary: also prefer reducing opponent's possible lead by moving closer
            # tertiary: avoid stepping into same line as opponent when tied
            lead = opd - myd
            opp_myd_now = cheb(ox, oy, sx, sy)
            key = (-lead, myd, abs(opd - myd), nx, ny, opp_myd_now)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]

    # No resources: increase control by moving toward center while keeping away from opponent
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_center = cheb(nx, ny, cx, cy)
        d_opp = cheb(nx, ny, ox, oy)
        key = (-d_opp, d_center, nx, ny)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1] if best is not None else [0, 0]