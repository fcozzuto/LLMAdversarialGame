def choose_move(observation):
    x0, y0 = observation["self_position"]
    xo, yo = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w, h = observation["grid_width"], observation["grid_height"]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Target selection: prefer resources opponent is closer to (deny/steal), else nearest.
    best = None
    best_score = -10**9
    for r in resources:
        dxr, dyr = r[0], r[1]
        if (dxr, dyr) in obstacles:
            continue
        d_self = dist((x0, y0), (dxr, dyr))
        d_opp = dist((xo, yo), (dxr, dyr))
        # Higher is better: prioritize positive gap where opponent is closer, then closer overall.
        score = (d_opp - d_self) * 10 - d_self
        if score > best_score:
            best_score = score
            best = (dxr, dyr)

    if best is None:
        return [0, 0]

    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = x0 + dx, y0 + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    # Aggressive local steering + avoid stepping into opponent if very close.
    opp_close = dist((x0, y0), (xo, yo)) <= 2
    bestm = None
    besth = None
    for dx, dy, nx, ny in moves:
        d_t = dist((nx, ny), (tx, ty))
        d_o = dist((nx, ny), (xo, yo))
        # If opponent is very close, slightly discourage decreasing opponent distance.
        h = d_t
        if opp_close:
            h += (-d_o) * 0.5  # smaller is better; negative d_o increases h when d_o decreases
        # Tie-break deterministically by lexicographic move order (dx,dy) preference.
        tup = (h, dx, dy)
        if besth is None or tup < besth:
            besth = tup
            bestm = (dx, dy)

    return [bestm[0], bestm[1]]