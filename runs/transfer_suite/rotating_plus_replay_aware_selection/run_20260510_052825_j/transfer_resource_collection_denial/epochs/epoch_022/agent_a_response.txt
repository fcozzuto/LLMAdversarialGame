def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    valid = []
    for r in resources:
        x, y = r[0], r[1]
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    tr = observation.get("turns_remaining", 0)
    remaining = observation.get("remaining_resource_count", len(valid))
    few = (tr <= 6) or (remaining <= 3)

    best_target = None
    best_val = -10**18
    for rx, ry in valid:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        lead = od - sd  # positive if we are closer
        # Encourage quicker grabs when possible; otherwise take winning leads.
        val = lead * 2.2 + (1.8 if sd <= 1 else 0.0) - sd * (0.45 if not few else 0.2)
        # Slightly prefer higher (rx,ry) centrality to avoid long detours.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        central = -(abs(rx - cx) + abs(ry - cy)) * (0.03 if few else 0.02)
        val += central
        if val > best_val:
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # Score moves by how much they improve our distance to target while preserving competition.
    best_move = (0, 0)
    best_ms = -10**18
    for dx, dy, nx, ny in candidates:
        nsd = man(nx, ny, tx, ty)
        nod = man(ox, oy, tx, ty)
        # Also account for possible immediate capture priority.
        capture_bonus = 2.3 if nsd <= 0 else (1.3 if nsd == 1 else 0.0)
        # Discourage steps that worsen lead too much.
        lead_now = nod - nsd
        ms = lead_now * 1.8 - nsd * (0.8 if not few else 0.55) + capture_bonus
        # Micro tie-break: prefer diagonal when it helps.
        ms += (0.05 if dx != 0 and dy != 0 else 0.0)
        if ms > best_ms:
            best_ms = ms
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]