def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    grid_w, grid_h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Prefer resources we can reach earlier; if close, pick higher "choke" value via remaining count
    best = None
    best_key = None
    for rx, ry in resources:
        sd = manh(rx, ry, sx, sy)
        od = manh(rx, ry, ox, oy)
        # primary: maximize (od - sd); secondary: smaller sd; tertiary: deterministic preference by coordinates
        key = (od - sd, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key, best = key, (rx, ry)
    tx, ty = best

    # Desired greedy direction
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    # If the direct step is blocked, try nearby options in a deterministic order
    candidates = []
    # Order prefers moves that reduce distance to target first, then toward dx0/dy0
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < grid_w and 0 <= ny < grid_h):
                continue
            if (nx, ny) in obstacles:
                continue
            if dx == 0 and dy == 0:
                pass
            nd = manh(nx, ny, tx, ty)
            # Prefer equal/closer distance, then alignment with greedy direction, then deterministic coords
            align = -(abs(dx - dx0) + abs(dy - dy0))
            key = (-nd, align, -nx, -ny)
            candidates.append((key, [dx, dy]))

    if not candidates:
        # Nowhere to go except staying (or we'd be forced into obstacle by engine)
        return [0, 0]

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]