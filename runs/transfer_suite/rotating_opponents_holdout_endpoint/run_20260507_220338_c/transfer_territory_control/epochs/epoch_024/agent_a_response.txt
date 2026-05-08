def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    my = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    un = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    if (sx, sy) in obstacles:
        obstacles.discard((sx, sy))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-10**18, (0, 0))

    # Precompute nearby targets deterministically
    targets = []
    for x, y in un:
        targets.append((abs(x - sx) + abs(y - sy), x, y, 1))
    for x, y in opp:
        # Only consider opponent territory near us (reduces flips chase)
        d = abs(x - sx) + abs(y - sy)
        if d <= 6:
            targets.append((d, x, y, 2))
    targets.sort(key=lambda t: (t[0], t[1], t[2]))
    targets = targets[:16]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        gain = 0
        if (nx, ny) in un:
            gain = 1
        elif (nx, ny) in opp:
            gain = 1  # flipping on entry

        # Safety: prefer staying away from opponent
        dist_opp = abs(nx - ox) + abs(ny - oy)

        # Advancement: prefer moving closer to the best nearby target (unclaimed first)
        best_adv = 10**9
        best_adv_is_opp = 0
        for _, tx, ty, ttype in targets:
            d = abs(tx - nx) + abs(ty - ny)
            if d < best_adv or (d == best_adv and ttype > best_adv_is_opp):
                best_adv = d
                best_adv_is_opp = ttype

        # Centering to avoid edge traps (territory_edge_claim archetype)
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_dist = abs(nx - cx) + abs(ny - cy)

        # Edge penalty
        edge_pen = (nx == 0) + (ny == 0) + (nx == w - 1) + (ny == h - 1)

        score = (
            gain * 1000
            + dist_opp * 2
            - best_adv
            - center_dist * 0.3
            - edge_pen * 3
        )

        if (score, (dx, dy)) > best:
            best = (score, (dx, dy))

    return [int(best[1][0]), int(best[1][1])]