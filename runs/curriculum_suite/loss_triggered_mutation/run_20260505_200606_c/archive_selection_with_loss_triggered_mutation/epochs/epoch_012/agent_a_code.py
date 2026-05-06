def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return (x, y) not in obstacles
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    def best_escape():
        bestv = -10**18
        best = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or not ok(nx, ny):
                continue
            d = man(nx, ny, ox, oy)
            cx = nx - (w - 1) / 2.0
            cy = ny - (h - 1) / 2.0
            center = -(cx*cx + cy*cy)
            v = d*10 + center
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    if not resources:
        return best_escape()

    # Choose up to a few candidate resources deterministically
    cand = []
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources we can reach at least not much later than opponent
        # Add tie-break by coordinate order for determinism
        reach_adv = (do - ds)  # positive if we are closer
        score = reach_adv * 100 - ds * 2 + (rx*0.001 + ry*0.0001)
        cand.append((score, ds, rx, ry))
    cand.sort(reverse=True)
    top = cand[:min(4, len(cand))]

    bestv = -10**18
    best = [0, 0]

    # Evaluate moves against best threat target, with a small "denial" component
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or not ok(nx, ny):
            continue
        v = -man(nx, ny, ox, oy) * 0.05  # slightly prefer separating from opponent
        for _, _, tx, ty in top:
            ds_next = man(nx, ny, tx, ty)
            do_next = man(ox, oy, tx, ty)
            # If we are likely to beat them on this target, prioritize it strongly
            v += (do_next - ds_next) * 1.5 + ( -ds_next * 0.25 )
        # Also encourage moving toward any resource if targets ambiguous
        min_ds = 10**9
        for _, _, tx, ty in top:
            d = man(nx, ny, tx, ty)
            if d < min_ds:
                min_ds = d
        v += (30 - min_ds) * 0.2
        # Center bias tie-break
        cx = nx - (w - 1) / 2.0
        cy = ny - (h - 1) / 2.0
        v += -(cx*cx + cy*cy) * 0.01

        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best