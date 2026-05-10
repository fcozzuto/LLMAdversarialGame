def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_t = set((int(p[0]), int(p[1])) for p in observation.get("self_territory") or [])
    opp_t = set((int(p[0]), int(p[1])) for p in observation.get("opponent_territory") or [])
    unclaimed = set((int(p[0]), int(p[1])) for p in observation.get("unclaimed_cells") or [])

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = -10**18

    # Prefer: capturing adjacent opponent territory, then expanding into unclaimed, while steering to center.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        in_self = (nx, ny) in self_t
        in_opp = (nx, ny) in opp_t
        in_un = (nx, ny) in unclaimed

        dist_center = abs(nx - cx) + abs(ny - cy)

        # Encourage edge-battles: move that reduces distance to the nearest opponent cell (deterministic approx).
        # (Compute nearest opponent in a tiny radius for speed.)
        near_opp = 0
        r = 3
        for ax in range(nx - r, nx + r + 1):
            for ay in range(ny - r, ny + r + 1):
                if (ax, ay) in opp_t:
                    near_opp = max(near_opp, r - (abs(ax - nx) + abs(ay - ny)))
        opp_near_bonus = 0.0 if near_opp == 0 else 2.5 + 0.4 * near_opp

        val = 0.0
        if in_opp:
            val += 6.0  # flipping opponent territory is strongly beneficial
        if in_un:
            val += 2.0
        if in_self:
            val -= 0.1

        val += opp_near_bonus
        val += -0.45 * dist_center

        # Small deterministic tie-breaker: prefer moves that also reduce distance to opponent's current position (if known).
        ox, oy = observation.get("opponent_position", (sx, sy))
        val += -0.12 * (abs(nx - ox) + abs(ny - oy))

        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]