def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in observation.get("obstacles", [])}
    self_cells = observation.get("self_territory", []) or []
    opp_cells = observation.get("opponent_territory", []) or []
    myc = observation.get("self_territory_count", len(self_cells))
    opc = observation.get("opponent_territory_count", len(opp_cells))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []))
    myset = set(tuple(p) for p in self_cells)
    oppset = set(tuple(p) for p in opp_cells)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    aggressive = myc < opc

    adj8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    expand = set()
    steal = set()
    for (x, y) in myset:
        for dx, dy in adj8:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                expand.add((nx, ny))
    for (x, y) in oppset:
        for dx, dy in adj8:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                steal.add((nx, ny))

    opp_near = min([abs(ox - sx) + abs(oy - sy)], default=99)
    mode = "steal" if aggressive or opp_near <= 3 else "expand"

    def nearest(cset):
        best = None
        bestd = 10**9
        for (x, y) in cset:
            d = abs(x - sx) + abs(y - sy)
            if d < bestd or (d == bestd and (x, y) < best):
                bestd, best = d, (x, y)
        return best

    target = nearest(steal if mode == "steal" else expand)
    if target is None:
        target = nearest(expand if mode == "steal" else steal)  # fallback
    if target is None:
        if inb(sx + 1, sy) and (sx + 1, sy) not in obstacles: return [1, 0]
        return [0, 0]

    tx, ty = target
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = 0
        v -= (abs(tx - nx) + abs(ty - ny))
        if (nx, ny) in oppset: v += 20
        if (nx, ny) in unclaimed: v += 6 if (nx, ny) in (steal if aggressive else expand) else 2
        if (nx, ny) in expand: v += 2
        if (nx, ny) in steal: v += 4
        v += (-(abs(ox - nx) + abs(oy - ny))) * (2 if aggressive else 1)
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val, best_move = v, (dx, dy)
    return [int(best_move[0]), int(best_move[1])]