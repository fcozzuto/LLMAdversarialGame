def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (sx, sy)) or (sx, sy)

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                obs.add((x, y))

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                self_terr.add((x, y))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                opp_terr.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or observation.get("unclaimed") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y) and (x, y) not in obs:
                unclaimed.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_sc = -10**18

    opp_list = list(opp_terr)
    un_list = list(unclaimed)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        cell = (nx, ny)
        sc = 0

        if cell in opp_terr:
            sc += 1200
        elif cell in unclaimed:
            sc += 400
        elif cell in self_terr:
            sc += 40
        else:
            sc += 10

        # Prefer moving toward nearest valuable target; also slightly away from opponent to reduce their approach
        if un_list:
            d_un = min(abs(nx - ux) + abs(ny - uy) for ux, uy in un_list)
            sc += 50 - d_un
        if opp_list:
            d_opp = abs(nx - ox) + abs(ny - oy)
            sc += -0.8 * d_opp

        # Encourage expanding frontier: prefer cells adjacent to our territory when safe
        adj_self = 0
        for adx, ady in dirs:
            tx, ty = nx + adx, ny + ady
            if inside(tx, ty) and (tx, ty) in self_terr:
                adj_self += 1
        sc += 3 * adj_self

        # Deterministic tie-break: lexicographically smallest move among equals
        if sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]