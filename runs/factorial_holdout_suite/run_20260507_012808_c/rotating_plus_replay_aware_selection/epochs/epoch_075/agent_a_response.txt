def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    ox, oy = observation["opponent_position"]

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d(x1, y1, x2, y2):
        return max(abs(x2 - x1), abs(y2 - y1))  # Chebyshev

    def best_target():
        if not resources:
            return None
        best = None
        best_key = (-10**18, -10**18, 10**18)
        for rx, ry in resources:
            sd = d(sx, sy, rx, ry)
            od = d(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer or equal
            # Prefer taking resources where we are ahead; if tied, prefer closer overall.
            key = (adv, -(sd + od), sd)
            if key > best_key:
                best_key = key
                best = (rx, ry)
        return best

    target = best_target()
    if target is None:
        return [0, 0]

    tx, ty = target
    # Evaluate our immediate move by resulting advantage on the same target.
    best_move = [0, 0]
    best_key = (-10**18, 10**18, 10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd2 = d(nx, ny, tx, ty)
        od2 = d(ox, oy, tx, ty)  # opponent assumed to be on same target pressure this turn
        adv2 = od2 - sd2
        # Also gently encourage reducing overall risk of "giving up" by getting closer to some resource.
        # Pick nearest resource distance from new position.
        min_sd_any = 10**18
        for rx, ry in resources:
            md = d(nx, ny, rx, ry)
            if md < min_sd_any:
                min_sd_any = md
        key = (adv2, min_sd_any, sd2)
        if key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move