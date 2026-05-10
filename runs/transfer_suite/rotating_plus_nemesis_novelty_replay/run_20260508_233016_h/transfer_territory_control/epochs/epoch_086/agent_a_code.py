def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    if not unclaimed:
        # fallback: move toward center, but stay away from obstacles
        tx, ty = w // 2, h // 2
    else:
        # deterministic target among best frontier-like cells
        def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)
        # cells near opponent are valuable; cells near us are reachable; avoid deep inside opponent
        candidates = list(unclaimed)
        def key(c):
            x, y = c
            dso = man(x, y, ox, oy)
            dss = man(x, y, sx, sy)
            inopp = 1 if (x, y) in oppT else 0
            # favor cells with higher "edgeyness": unclaimed with many unclaimed neighbors
            neigh = 0
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0: continue
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in unclaimed: neigh += 1
            return (inopp * 10 + dss * 2 - dso, -neigh, x, y)
        best = sorted(candidates, key=key)[0]
        tx, ty = best
    # choose next step minimizing distance to target, maximizing potential capture
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def score_cell(nx, ny):
        if not (0 <= nx < w and 0 <= ny < h): return -10**9
        if (nx, ny) in obstacles: return -10**8
        # base: distance to target
        d = abs(nx - tx) + abs(ny - ty)
        # potential: how many unclaimed neighbors we'd unlock/expand into
        unlock = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: continue
                nn = (nx + dx, ny + dy)
                if nn in unclaimed: unlock += 1
        # territory type bias
        tbonus = 0
        if (nx, ny) in selfT: tbonus += 2
        elif (nx, ny) in oppT: tbonus += 1  # flipping on entry is enabled
        else: tbonus += 4  # unclaimed capture immediately
        # anti-stall near obstacles: discourage being adjacent to obstacles unless useful
        adj_obs = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: continue
                nn = (nx + dx, ny + dy)
                if nn in obstacles: adj_obs += 1
        return (tbonus * 10 + unlock * 3 - d * 2 - adj_obs)
    best_mv = (0, 0)
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = score_cell(nx, ny)
        # small deterministic preference: closer to opponent if tie, then lexicographic
        sc2 = sc + (0.001 * (-(abs(nx - ox) + abs(ny - oy))))
        if sc2 > best_sc or (sc2 == best_sc and (dx, dy) < best_mv):
            best_sc = sc2
            best_mv = (dx, dy)
    return [int(best_mv[0]), int(best_mv[1])]