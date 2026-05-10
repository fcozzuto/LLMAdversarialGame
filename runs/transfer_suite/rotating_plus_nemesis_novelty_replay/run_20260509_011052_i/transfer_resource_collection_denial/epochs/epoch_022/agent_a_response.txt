def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obs.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist_time(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_r = None
    best_key = None
    for r in resources:
        st = dist_time((sx, sy), r)
        ot = dist_time((ox, oy), r)
        # primary: can we arrive no later than opponent; secondary: maximize advantage
        # if both can't, prefer the one where opponent is worse relative to us
        can = 1 if st <= ot else 0
        adv = (ot - st)  # positive means we are earlier or equal
        key = (can, adv, -st, -ot)
        if best_key is None or key > best_key:
            best_key = key
            best_r = r

    tx, ty = best_r

    if (sx, sy) == (tx, ty):
        return [0, 0]

    # Choose next step that gets closer while avoiding obstacles deterministically.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            if (nx, ny) in obs:
                continue
            # Chebyshev distance to target
            ddx = abs(nx - tx)
            ddy = abs(ny - ty)
            d = ddx if ddx > ddy else ddy
            # Prefer steps that keep us competitive vs opponent for this target
            nt = dist_time((nx, ny), (tx, ty))
            tot = dist_time((ox, oy), (tx, ty))
            can = 1 if nt <= tot else 0
            candidates.append(((can, -(ot - nt), -d, -abs((nx - tx) + (ny - ty)), dx, dy), d, nx, ny, dx, dy))

    if not candidates:
        return [0, 0]

    # Deterministic pick by best key then smallest dx,dy lexicographically.
    best = None
    bestk = None
    for item in candidates:
        key = item[0]
        if bestk is None or key > bestk:
            bestk = key
            best = item
    return [int(best[4]), int(best[5])]