def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)

    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []) if p and len(p) >= 2)
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []) if p and len(p) >= 2)
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []) if p and len(p) >= 2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Precompute nearest unclaimed and nearest opponent cell (cheap O(n) over sets)
    opp_list = list(opp)
    un_list = list(unclaimed)

    best_target = None
    best_td = 10**9
    if opp_list and un_list:
        # Prefer unclaimed adjacent to opponent territory
        adj = []
        for ux, uy in un_list:
            for ox, oy in opp_list:
                if abs(ux - ox) <= 1 and abs(uy - oy) <= 1 and md(ux, uy, ox, oy) != 0:
                    adj.append((ux, uy))
                    break
        if adj:
            un_list = adj

    def score(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obs:
            return -10**12
        s = 0
        if (nx, ny) in unclaimed:
            s += 200
        if opp and any((nx + dx, ny + dy) in opp for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)):
            s += 120
        if (nx, ny) in selft:
            s += 10
        # Move toward nearest unclaimed if any, else toward opponent
        if un_list:
            td = 10**9
            for ux, uy in un_list:
                d = abs(nx - ux) + abs(ny - uy)
                if d < td:
                    td = d
            s -= 3 * td
        else:
            ox, oy = observation.get("opponent_position", [x, y])
            s -= 3 * (abs(nx - ox) + abs(ny - oy))
        # Discourage leaving board already handled; slightly prefer centerish stability
        s += -0.5 * md(nx, ny, x, y)
        return s

    best = None
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        sc = score(nx, ny)
        if sc > best_s or (sc == best_s and (best is None or (dx, dy) < best)):
            best_s = sc
            best = (dx, dy)

    return [best[0], best[1]]