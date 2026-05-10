def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    obs = set((x, y) for (x, y) in (observation.get("obstacles") or []) if inb(x, y))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    ox, oy = observation["opponent_position"]

    # If no unclaimed, fall back to expanding into opponent territory.
    targets = [p for p in unclaimed if inb(p[0], p[1])]
    if not targets:
        targets = [p for p in opp_terr if inb(p[0], p[1])]
    if not targets:
        return [0, 0]

    targets2 = targets
    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0
    tmax = 10
    if len(targets2) > tmax:
        # Prefer nearer to us and farther from opponent (deterministic truncation).
        targets2.sort(key=lambda p: (abs(p[0] - ax) + abs(p[1] - ay), -(abs(p[0] - ox) + abs(p[1] - oy)), p[0], p[1]))
        targets2 = targets2[:tmax]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny, dx, dy = ax, ay, 0, 0

        npos = (nx, ny)
        base = 0
        if npos in unclaimed:
            base += 4.0
        elif npos in opp_terr:
            base += 2.5  # flipping enabled
        elif npos in self_terr:
            base += 0.3

        # Gain from proximity to best target
        md = 10**9
        for px, py in targets2:
            d = abs(nx - px) + abs(ny - py)
            if d < md:
                md = d
        # Encourage moving away from opponent slightly while still approaching targets
        oppd = abs(nx - ox) + abs(ny - oy)
        cen = -abs(nx - center_x) - abs(ny - center_y)

        val = base + (3.0 / (1.0 + md)) + 0.01 * oppd + 0.001 * cen
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]