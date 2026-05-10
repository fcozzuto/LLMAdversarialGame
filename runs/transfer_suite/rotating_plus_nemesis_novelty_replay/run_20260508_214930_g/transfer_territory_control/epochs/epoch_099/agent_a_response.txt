def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Target: nearest unclaimed, else push toward boundary away from opponent
    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    else:
        # Prefer moving toward farthest corner from opponent (deterministic)
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy), c[0], c[1]))

    def score_cell(nx, ny):
        d = abs(nx - tx) + abs(ny - ty)
        # Base: reduce distance to target
        sc = 120 - 2 * d

        if (nx, ny) in unclaimed:
            sc += 45
        if (nx, ny) in self_t:
            sc += 12
        if (nx, ny) in opp_t:
            sc += 80  # flipping on entry
            sc -= 6 * (abs(nx - ox) + abs(ny - oy) == 1)  # slight caution when adjacent

        # Avoid adjacency to opponent's territory to reduce getting swept back
        # (Territory is small, so compute locally)
        adj_pen = 0
        for dx, dy in dirs:
            ax, ay = nx + dx, ny + dy
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in opp_t:
                adj_pen += 1
        sc -= 10 * adj_pen

        # Keep moving instead of dithering if possible
        if (nx, ny) == (sx, sy):
            sc -= 8

        return sc

    best = (0, 0)
    best_sc = -10**18
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue
        sc = score_cell(nx, ny)
        # Tie-break deterministically: prefer staying in bounds and moving closer to target; then lexicographic
        tie = (abs(nx - tx) + abs(ny - ty), nx, ny)
        if sc > best_sc or (sc == best_sc and tie < (abs(best[0] + sx - tx) + abs(best[1] + sy - ty), best[0] + sx, best[1] + sy)):
            best_sc = sc
            best = (ddx, ddy)

    return [int(best[0]), int(best[1])]