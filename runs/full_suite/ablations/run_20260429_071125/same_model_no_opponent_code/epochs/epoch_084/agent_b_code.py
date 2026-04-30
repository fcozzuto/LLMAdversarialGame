def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    turn = int(observation.get("turn_index", 0) or 0)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
    # Deterministic "mode" shift to vary choices without randomness
    mode = (turn + rem + (sx + sy) + (ox + oy)) % 3

    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    best_t = None
    best_v = None
    for x, y in resources:
        ds = man(sx, sy, x, y)
        do = man(ox, oy, x, y)
        # Prefer resources where we are (or will be) earlier than opponent; also prefer being closer.
        adv = do - ds  # positive => we can reach earlier
        v = adv * 10 - ds
        if mode == 0:
            v += (1 if x == sx or y == sy else 0)
        elif mode == 1:
            v += (2 if (x - sx) * (y - sy) >= 0 else 0)
        else:
            v += (1 if (x + y) <= (w - 1) + (h - 1) // 2 else 0)
        if best_v is None or v > best_v or (v == best_v and (x, y) < best_t):
            best_v = v
            best_t = (x, y)

    tx, ty = best_t

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            ds = man(nx, ny, tx, ty)
            do = man(ox, oy, tx, ty)
            # If we move closer to target, reward; also keep advantage vs opponent.
            val = (do - ds) * 10 - ds
            # Mild tie-break: move toward target more than sideways drifting.
            val += -abs(tx - nx) - abs(ty - ny)
            candidates.append((val, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]