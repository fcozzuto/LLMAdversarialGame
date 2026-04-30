def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    # Choose target resource: prefer ones we are closer to than opponent (and not blocked by being too close)
    best = None
    best_val = -10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        val = (do - ds) * 10 - ds
        # Mild preference for resources nearer to our side early game
        val += -(rx + ry) * 0.01
        if val > best_val:
            best_val = val
            best = (rx, ry)
    if best is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best
    # Evaluate candidate moves; deterministic tie-breaking by fixed delta order
    candidates = []
    order = [(0, 0), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Keep an eye on opponent: avoid moving into squares that allow immediate capture-like closeness
        d_self = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(tx - ox) + abs(ty - oy)
        # If opponent is close to our target, try to reduce our distance further
        score = -d_self * 100 + (d_opp - (abs(tx - ox) + abs(ty - oy))) * 0 + (-(abs(nx - ox) + abs(ny - oy)) * 0.1)
        # Deterministic priority: prefer bigger score, then smaller Manhattan to target, then fixed order
        candidates.append((score, d_self, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
    _, _, mdx, mdy = candidates[0]
    return [int(mdx), int(mdy)]