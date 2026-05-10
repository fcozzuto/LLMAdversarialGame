def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    neigh4 = [(-1,0),(1,0),(0,-1),(0,1)]
    neigh8 = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def adj_to_opp(cx, cy):
        for dx, dy in neigh4:
            tx, ty = cx + dx, cy + dy
            if inb(tx, ty) and (tx, ty) in oppT:
                return True
        return False

    def adj_to_self(cx, cy):
        for dx, dy in neigh4:
            tx, ty = cx + dx, cy + dy
            if inb(tx, ty) and (tx, ty) in selfT:
                return True
        return False

    def score_cell(cx, cy):
        if (cx, cy) in obstacles:
            return -10**9
        if (cx, cy) in selfT:
            base = 0.0
        elif (cx, cy) in oppT:
            base = 3.5  # likely flipping on entry
        elif (cx, cy) in unclaimed:
            base = 1.8
        else:
            base = 0.2  # boundary/unknown
        bonus = 0.0
        if (cx, cy) in unclaimed and adj_to_opp(cx, cy):
            bonus += 3.2  # aggressive counter-claim
        if (cx, cy) in unclaimed and adj_to_self(cx, cy):
            bonus += 1.0  # safer expansion
        d_opp = abs(cx - ox) + abs(cy - oy)
        if oppT:
            # center-ish bias: prefer moving toward opponent when close to them
            bonus += 1.0 / (1 + d_opp)
        return base + bonus

    best = None
    bestv = -10**18
    # deterministic tie-break preference: closer to opponent, then toward center-ish
    center_bias = 0.0
    if selfT:
        sx = sy = 0
        for px, py in selfT:
            sx += px; sy += py
        center_bias = -0.001 * (sx/len(selfT) - (w-1)/2) ** 2

    for dx, dy in neigh8:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = x, y
            dx, dy = 0, 0
        v = score_cell(nx, ny)
        v += center_bias
        v += 0.01 * (-(abs(nx - ox) + abs(ny - oy)))
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]