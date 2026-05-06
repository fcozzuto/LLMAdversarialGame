def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        best = None
        bestd = -10**9
        for dx, dy, nx, ny in moves:
            d = man((nx, ny), (ox, oy))
            if d > bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    # Target selection: prefer resources where we are closer than opponent; otherwise closest reachable-ish.
    best_r = None
    best_score = -10**18
    for r in resources:
        sd = man((sx, sy), r)
        od = man((ox, oy), r)
        # if we are ahead (od - sd > 0), prioritize it strongly; otherwise, still consider but weakly.
        score = (od - sd) * 1000 - sd
        # deterministic tie-break: lexicographic by coordinates
        if score > best_score or (score == best_score and r < best_r):
            best_score = score
            best_r = r

    tx, ty = best_r

    # Move selection: greedily improve target distance while maintaining advantage over opponent.
    best = None
    best_h = -10**18
    for dx, dy, nx, ny in moves:
        myd = man((nx, ny), (tx, ty))
        oppd = man((ox, oy), (tx, ty))
        curd = man((sx, sy), (tx, ty))
        # advantage after move; also penalize moving away from target
        adv_after = oppd - myd
        h = adv_after * 1000 - myd - (myd - curd) * 10
        # slight bias to progress toward staying away from obstacles in corners
        corner_bias = - (nx == 0 or nx == gw - 1) - (ny == 0 or ny == gh - 1)
        h += corner_bias
        if h > best_h or (h == best_h and (dx, dy) < best):
            best_h = h
            best = (dx, dy)
    return [int(best[0]), int(best[1])]