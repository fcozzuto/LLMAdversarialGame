def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Pick a target resource that we can contest quickly, with extra pressure on opponent-aligned lanes.
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        contest = od - sd  # >0 means we're closer
        align = 0
        if ry == oy: align += 2
        if rx == ox: align += 1
        # Prefer closer overall but keep contest priority.
        key = (-(contest * 10 + align), sd, rx * 8 + ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)

    _, tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_val = None

    # If we're losing contests hard, bias toward reducing distance to the closest threatening resource.
    # Otherwise, greedily minimize distance to target.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_target = man(nx, ny, tx, ty)

        # Safety/obstacle pressure: avoid stepping into positions that increase distance for both.
        self_to_opp = man(nx, ny, ox, oy)
        opp_d = min(man(ox, oy, rx, ry) for rx, ry in resources) if resources else 999

        # Greedy objective with deterministic tie-break.
        # Slightly prefer staying nearer to opponent-aligned direction when contesting.
        align_bias = 0
        if ty == oy: align_bias += 1
        if tx == ox: align_bias += 0

        # If we are currently farther than opponent to target, emphasize decreasing distance to target more.
        cur_sd = man(sx, sy, tx, ty)
        cur_od = man(ox, oy, tx, ty)
        pressure = 5 if cur_sd > cur_od else 2

        val = (d_to_target * pressure + self_to_opp * 0 - align_bias, d_to_target, self_to_opp, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move