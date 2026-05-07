def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = ox, oy
        best = [0, 0]
        bestd = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = abs(nx - tx) + abs(ny - ty)
            if bestd is None or d < bestd:
                bestd = d
                best = [dx, dy]
        return best

    # Choose a "primary" resource to contest: the one closest to us (tie -> lower opponent distance)
    primary = None
    for rx, ry in resources:
        ds = abs(sx - rx) + abs(sy - ry)
        do = abs(ox - rx) + abs(oy - ry)
        key = (ds, do, rx, ry)
        if primary is None or key < primary[0]:
            primary = (key, (rx, ry))
    rx, ry = primary[1]

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Base: minimize our distance to the contested resource; strong bonus for stepping onto any resource.
        my_d = abs(nx - rx) + abs(ny - ry)
        on_resource_bonus = 0
        for rr in resources:
            if rr[0] == nx and rr[1] == ny:
                on_resource_bonus = 10
                break

        # Denial: after our move, prefer being closer than opponent would be to the contested resource.
        opp_d = abs(ox - rx) + abs(oy - ry)
        # Estimate opponent immediate improvement by moving one step towards contested resource.
        od_next = min(
            (abs((ox + adx) - rx) + abs((oy + ady) - ry))
            for adx in (-1, 0, 1) for ady in (-1, 0, 1)
            if inb(ox + adx, oy + ady) or (0 <= ox + adx < w and 0 <= oy + ady < h and (ox + adx, oy + ady) not in obstacles)
        )

        # If we gain relative closeness this turn, reward; if we fall behind, penalize.
        rel_gain = (opp_d - od_next) - (my_d - (abs(sx - rx) + abs(sy - ry)))
        denial = 3.0 if my_d <= od_next else -1.5

        # Secondary: slight preference for reducing distance to the next-best resource if contested doesn't pan out.
        other_best = 999
        for r2x, r2y in resources:
            if (r2x, r2y) == (rx, ry):
                continue
            d2 = abs(nx - r2x) + abs(ny - r2y)
            if d2 < other_best:
                other_best = d2

        score = (-my_d) + on_resource_bonus + 0.15 * (-other_best) + 0.2 * rel_gain + denial
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move