def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    self_set = set(tuple(p) for p in observation.get("self_territory") or [])
    opp_set = set(tuple(p) for p in observation.get("opponent_territory") or [])
    un_set = set(tuple(p) for p in observation.get("unclaimed_cells") or [])

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    candidates = [(sx + dx, sy + dy, dx, dy) for dx, dy in dirs]
    candidates = [c for c in candidates if inb(c[0], c[1]) and (c[0], c[1]) not in blocked]

    def neighbors(x, y):
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0: 
                    continue
                nx, ny = x + ddx, y + ddy
                if 0 <= nx < w and 0 <= ny < h:
                    yield nx, ny

    # Precompute nearest unclaimed distance (small grid; keep deterministic).
    un_list = [(x, y) for (x, y) in un_set if inb(x, y)]
    if un_list:
        nearest_un = min(un_list, key=lambda t: abs(t[0]-sx) + abs(t[1]-sy))
    else:
        nearest_un = (w//2, h//2)

    best = None
    best_u = None
    tie = 0
    for nx, ny, dx, dy in candidates:
        u = 0
        if (nx, ny) in self_set: u += 1
        if (nx, ny) in un_set: u += 6
        if (nx, ny) in opp_set: u += 4  # allow counterclaim capture via flipping

        # Encourage expanding from our frontier; discourage deep into enemy mass.
        adj_self = 0
        for axx, ayy in neighbors(nx, ny):
            if (axx, ayy) in self_set: adj_self += 1
        u += adj_self * 2

        adj_opp = 0
        for axx, ayy in neighbors(nx, ny):
            if (axx, ayy) in opp_set: adj_opp += 1
        u -= adj_opp * 0.5

        # Move towards the closest unclaimed overall.
        u += -(abs(nx - nearest_un[0]) + abs(ny - nearest_un[1])) * 0.1

        # Slightly prefer moves that are not directly towards opponent (reduce being countered).
        u += (abs(nx - ox) + abs(ny - oy)) * 0.02

        if best_u is None or u > best_u or (u == best_u and tie < 1e-9):
            best_u = u
            best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]