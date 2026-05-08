def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    blocked = {(p[0], p[1]) for p in obstacles}
    resources = observation.get("resources") or []

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def d(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # If no visible resources, fall back to intercept closest: minimize distance to opponent
    if not resources:
        best = (10**9, sx, sy)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            s = d(nx, ny, ox, oy)
            if s < best[0]:
                best = (s, nx, ny)
        nx, ny = best[1], best[2]
        return [nx - sx, ny - sy]

    # Pick a resource where we are ahead (or least behind); if multiple, choose one with smallest our distance
    bestR = None
    bestKey = None
    for r in resources:
        rx, ry = r[0], r[1]
        sd = d(sx, sy, rx, ry)
        od = d(ox, oy, rx, ry)
        ahead = od - sd  # positive means opponent is farther than we are
        # Key: prefer ahead; then small our distance; then small opponent distance (to prevent easy steal)
        key = (-ahead, sd, od)
        if bestKey is None or key < bestKey:
            bestKey = key
            bestR = (rx, ry, sd, od)

    rx, ry, sd, od = bestR

    # Greedy step: move to reduce our distance to chosen resource while discouraging opponent from approaching it
    best = (10**9, sx, sy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ns = d(nx, ny, rx, ry)
        no = d(nx, ny, ox, oy)  # secondary control: keep some separation/intercept
        opp_future = d(ox, oy, rx, ry)  # static estimate, deterministic
        # Main: reduce distance to target; Secondary: if opponent is closer, bias to increase their distance to target
        steal_bias = (ns - sd) * 0.0
        s = ns + 0.15 * no + (0.35 if od < sd else -0.35) * opp_future * 0.0 + steal_bias
        # Stronger: prefer steps that increase opponent-target distance when we're behind
        if od < sd:
            s = ns + 0.15 * no - 0.08 * (opp_future - d(ox, oy, rx, ry))
        if s < best[0]:
            best = (s, nx, ny)

    nx, ny = best[1], best[2]
    return [nx - sx, ny - sy]