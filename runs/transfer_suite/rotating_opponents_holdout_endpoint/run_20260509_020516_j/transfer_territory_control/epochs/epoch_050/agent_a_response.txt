def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    myT = set((int(t[0]), int(t[1])) for t in (observation.get("self_territory") or []) if t and len(t) >= 2)
    oppT = set((int(t[0]), int(t[1])) for t in (observation.get("opponent_territory") or []) if t and len(t) >= 2)
    unC = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2)

    def inb(x, y): return 0 <= x < W and 0 <= y < H

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    # Build opponent-adjacent and unclaimed-frontier "hotspots"
    opp_hot = set()
    for ox, oy in oppT:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    x, y = ox + dx, oy + dy
                    if inb(x, y) and (x, y) in unC:
                        opp_hot.add((x, y))
    my_front = set()
    for mx, my in myT:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    x, y = mx + dx, my + dy
                    if inb(x, y) and (x, y) in unC:
                        my_front.add((x, y))

    target_list = []
    if opp_hot:
        target_list = list(opp_hot)
    elif my_front:
        target_list = list(my_front)
    else:
        target_list = list(unC)

    # Choose move by local scoring with deterministic tie-breaking
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        score = 0.0
        if (nx, ny) in oppT:
            score += 1000.0
        if (nx, ny) in myT:
            score += 1.0
        if (nx, ny) in unC:
            score += 120.0
        # Encourage moving toward best hotspot
        if target_list:
            dmin = 10**9
            for tx, ty in target_list[:40]:
                dd = abs(tx - nx) + abs(ty - ny)
                if dd < dmin:
                    dmin = dd
            score += max(0.0, 60.0 - 6.0 * dmin)
        # Slightly prefer center to reduce stagnation
        cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
        score += -0.15 * (abs(nx - cx) + abs(ny - cy))
        # Avoid edges if not needed
        score += -0.05 * (nx == 0 or nx == W - 1 or ny == 0 or ny == H - 1)

        key = (-score, dx, dy)  # deterministic tie-break: higher score first, then dx,dy
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]