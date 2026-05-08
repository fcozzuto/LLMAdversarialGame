def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    self_terr = to_set("self_territory")
    opp_terr = to_set("opponent_territory")

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def neigh(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    yield nx, ny

    # If we can, contest the opponent border: unclaimed cells adjacent to their territory.
    opp_border = set()
    if opp_terr:
        for ax, ay in opp_terr:
            for nx, ny in neigh(ax, ay):
                if (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                    opp_border.add((nx, ny))
    # If no border, grab nearest unclaimed (or opponent cell if everything claimed).
    targets = list(opp_border) if opp_border else list(unclaimed)
    if not targets:
        targets = list(opp_terr) if opp_terr else [(ox, oy)]

    # Score targets: prefer closer to us, and also closer to opponent (to squeeze/steal).
    best = None
    best_sc = -10**18
    for tx, ty in targets:
        if (tx, ty) in obstacles:
            continue
        ds = max(1, (abs(tx - sx) + abs(ty - sy)))
        do = max(1, (abs(tx - ox) + abs(ty - oy)))
        on_self = 1 if (tx, ty) in self_terr else 0
        sc = (50.0 / ds) + (15.0 / do) + (5.0 if on_self else 0.0)
        # Slightly prefer advancing generally toward the center if stuck.
        sc += -0.01 * (abs(tx - (w // 2)) + abs(ty - (h // 2)))
        if sc > best_sc:
            best_sc, best = sc, (tx, ty)

    if not best:
        return [0, 0]
    tx, ty = best

    # Move one step (including diagonal) that most improves reach to target.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_d = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d = abs(tx - nx) + abs(ty - ny)
        # If equidistant, prefer moves closer to opponent border pressure.
        if d < best_d:
            best_d, best_m = d, (dx, dy)
        elif d == best_d:
            if (abs(nx - ox) + abs(ny - oy)) < (abs(sx - ox) + abs(sy - oy)):
                best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]