def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None:
            continue
        x, y = p
        obstacles.add((int(x), int(y)))

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    # If nothing known, just move towards board center.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_cell(x, y):
        # Base for ownership state
        if (x, y) in opp_t:
            base = 6.0  # steal on entry (flipping enabled)
        elif (x, y) in unclaimed:
            base = 3.5
        elif (x, y) in self_t:
            base = 1.0
        else:
            base = 0.5

        # Encourage expansion: prefer proximity to unclaimed
        d_un = 999
        if unclaimed:
            # Local heuristic: nearest of a few via projection
            # (iterate all is fine: at most 64)
            for ux, uy in unclaimed:
                d = abs(ux - x) + abs(uy - y)
                if d < d_un:
                    d_un = d
        else:
            d_un = abs(x - cx) + abs(y - cy)
        base += 2.0 / (1 + d_un)

        # Discourage getting trapped near obstacles (soft penalty)
        # Count blocked neighbors around target.
        block = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                block += 1
        base -= 0.15 * block
        return base

    best = None
    best_sc = -10**18
    # Deterministic tie-break: prefer moves with smaller lexicographic order.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = score_cell(nx, ny)

        # Nudge: if can capture directly, also prefer moves that reduce distance to opponent territory.
        # Use opponent territory proximity if available.
        if opp_t:
            d_to_opp = 999
            for ax, ay in opp_t:
                d = abs(ax - nx) + abs(ay - ny)
                if d < d_to_opp:
                    d_to_opp = d
            sc += 1.0 / (1 + d_to_opp)

        if sc > best_sc or (sc == best_sc and (best is None or (dx, dy) < best)):
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]