def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h
    neigh8 = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if oppT:
        sx = sy = 0
        n = len(oppT)
        for px, py in oppT:
            sx += px; sy += py
        ocx, ocy = sx // n, sy // n
    else:
        ocx, ocy = ox, oy

    def boundary_bias(cx, cy):
        # If we're adjacent to opponent territory, moving there helps contest.
        adj_opp = 0
        adj_self = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            tx, ty = cx + dx, cy + dy
            if inb(tx, ty) and (tx, ty) in oppT: adj_opp += 1
            if inb(tx, ty) and (tx, ty) in selfT: adj_self += 1
        return adj_self - adj_opp

    best = None
    best_sc = -10**18
    for dx, dy in neigh8:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            sc = -10**12
        else:
            sc = 0
            if (nx, ny) in oppT:
                sc += 2.2  # flipping into opponent-owned cell
            elif (nx, ny) in unclaimed:
                sc += 1.4  # claiming an unclaimed cell
            elif (nx, ny) in selfT:
                sc += 0.3  # consolidation
            else:
                sc += 0.2  # unknown/unlisted cell: slight incentive to explore anyway

            sc += 0.9 * boundary_bias(nx, ny)

            # Slight pressure toward opponent's centroid to keep territory advantage
            sc += -0.02 * (abs(nx - ocx) + abs(ny - ocy))

            # Mild preference to avoid immediate standing still when other claims exist
            if dx == 0 and dy == 0:
                sc -= 0.05

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]