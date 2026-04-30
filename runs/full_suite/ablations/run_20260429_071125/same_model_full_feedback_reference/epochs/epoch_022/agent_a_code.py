def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles or not resources:
        return [0, 0]

    def dist_manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    resources.sort(key=lambda r: (r[0] * 13 + r[1] * 7))

    best_move = (0, 0)
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate by best target resource after this move.
        # Primary: how much sooner we can reach than opponent (bigger is better).
        # Secondary: our distance to that target (smaller is better).
        # Tertiary: keep determinism with target position order.
        local_best = None
        for rx, ry in resources:
            our_d = dist_manh(nx, ny, rx, ry)
            opp_d = dist_manh(ox, oy, rx, ry)
            lead = opp_d - our_d
            key = (lead, -our_d, -(rx * 31 + ry * 17))
            if (local_best is None) or (key > local_best):
                local_best = key

        if local_best is None:
            continue

        # Small bias toward staying closer to the overall center of remaining resources
        # (reduces oscillation) without heavy search.
        # Use fixed deterministic center from resource average (floor).
        cx = sum(r[0] for r in resources) // len(resources)
        cy = sum(r[1] for r in resources) // len(resources)
        center_bias = -dist_manh(nx, ny, cx, cy)

        move_key = (local_best[0], local_best[1], local_best[2], center_bias)
        if best_key is None or move_key > best_key:
            best_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]