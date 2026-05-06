def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 10**9, 0, 0)
        bx, by = sx, sy
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = man(nx, ny, cx, cy)
            if (d, abs(nx - ox) + abs(ny - oy), dx, dy) < (best[0], best[1], best[2], best[3]):
                best = (d, abs(nx - ox) + abs(ny - oy), dx, dy)
                bx, by = nx, ny
        return [best[2], best[3]]

    # Target selection: maximize "catch advantage" against opponent; then prefer shorter self distance and center control.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd  # bigger is better
        # Encourage staying aligned with likely sweep: reduce opponent-y influence by prioritizing resources with similar row/col dynamics.
        center_pen = abs(rx - cx) + abs(ry - cy)
        # Key: highest advantage, then smallest self distance, then closest to center (lower penalty), then deterministic tie by coords.
        key = (-(adv), sd, center_pen, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r

    # Choose next step that maximizes advantage for reaching that target and avoids giving opponent an immediate win.
    best_move = [0, 0]
    best_tuple = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nsd = man(nx, ny, rx, ry)
        nod = man(ox, oy, rx, ry)  # opponent unchanged this turn for greedy estimate
        nadv = nod - nsd
        # If opponent is closer to some other resource, try to keep that from happening by keeping self near the chosen target.
        # Primary objective: minimize self distance and maximize advantage.
        tup = (-nadv, nsd, abs(nx - cx) + abs(ny - cy), abs(nx - ox) + abs(ny - oy), dx, dy)
        if best_tuple is None or tup < best_tuple:
            best_tuple = tup
            best_move = [dx, dy]

    return best_move