def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target: prefer resources where we are closer than opponent (using Manhattan),
    # but break ties deterministically toward positions that are "later" in a scan order.
    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        key = (do - ds, -ds, -(rx * 9 + ry))  # deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    best_move = [0, 0]
    best_val = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue

            # primary: reduce distance to target (Manhattan)
            d_to = manh(nx, ny, tx, ty)
            # secondary: discourage giving opponent an easy approach (increase their distance)
            d_opp = manh(ox, oy, tx, ty)
            # discourage stepping into moves that make opponent likely to intercept: keep distance from opponent
            d_self_opp = manh(nx, ny, ox, oy)

            # If we move closer to target while also increasing our separation from opponent, score improves.
            val = (-d_to, d_self_opp, -d_opp, -((nx + 3) * 11 + (ny + 5)))
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    # If all candidate moves invalid (rare), stay put.
    return best_move if best_move in ([dx, dy] for dx in (-1, 0, 1) for dy in (-1, 0, 1)) else [0, 0]