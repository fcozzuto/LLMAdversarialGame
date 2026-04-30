def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [W - 1, H - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []) if p and len(p) >= 2)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    valid_res = [(r[0], r[1]) for r in resources if (r and len(r) >= 2 and (r[0], r[1]) not in obstacles)]
    if not valid_res:
        tx, ty = (W - 1 if sx < W // 2 else 0), (H - 1 if sy < H // 2 else 0)
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = man((nx, ny), (tx, ty))
            if best is None or d < best[0] or (d == best[0] and (dx, dy) < best[1]):
                best = (d, (dx, dy))
        return [best[1][0], best[1][1]]

    # Pick a contestable target deterministically: prefer resources where we are not too behind.
    # Score key: (who is closer bucket, our distance, opponent distance, coords)
    best_target = None
    for rx, ry in valid_res:
        ds = man((sx, sy), (rx, ry))
        do = man((ox, oy), (rx, ry))
        bucket = 0 if ds <= do else 1
        key = (bucket, ds, do, rx, ry)
        if best_target is None or key < best_target:
            best_target = key
            tgt = (rx, ry)

    tx, ty = tgt

    # Evaluate each move by resulting advantage around the target; include obstacle-safe bonus near target.
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds2 = man((nx, ny), (tx, ty))
        do2 = man((ox, oy), (tx, ty))
        # If we move onto a resource, prioritize heavily.
        hit = 1 if (nx, ny) == (tx, ty) else 0
        # Bonus for moving to positions closer than opponent by margin.
        adv = (do2 - ds2)
        # Mild tie-break: prefer shorter path overall and toward center slightly.
        center = man((nx, ny), (W // 2, H // 2))
        key = (-hit, -adv, ds2, center, dx, dy)
        if best is None or key < best:
            best = key
    return [best[3], best[4]]