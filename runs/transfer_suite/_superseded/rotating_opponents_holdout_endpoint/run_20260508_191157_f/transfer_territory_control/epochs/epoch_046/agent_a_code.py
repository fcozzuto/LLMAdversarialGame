def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (0, 0))

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    # Target favors center while also pressuring opponent-side of center.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    # If opponent is on one side, bias target slightly away from our corner and toward their side.
    bias_x = (ox - sx)
    bias_y = (oy - sy)
    tx = cx + (0.25 if bias_x > 0 else (-0.25 if bias_x < 0 else 0.0))
    ty = cy + (0.25 if bias_y > 0 else (-0.25 if bias_y < 0 else 0.0))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Deterministic tie-break order: prefer toward +x then +y then staying.
    moves.sort(key=lambda m: (-(m[0] == 1), -(m[1] == 1), m[0], m[1]))

    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        cell = (nx, ny)

        # Base: prefer closeness to strategic target (center pressure).
        d_target = abs(nx - tx) + abs(ny - ty)
        score = -3.0 * d_target

        # Territory dynamics.
        if cell in opp_t:
            score += 260.0  # flipping on entry
        elif cell in self_t:
            score += 28.0   # consolidate
        elif cell in unclaimed:
            score += 85.0   # expansion

        # Frontline effect: encourage moving to cells adjacent to opponent territory.
        adj_opp = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in opp_t:
                    adj_opp += 1
        score += 10.0 * adj_opp

        # Mild anti-stall near opponent: reduce distance to opponent if it doesn't hurt target pressure.
        score += -1.5 * (abs(nx - ox) + abs(ny - oy)) / 2.0

        # Avoid getting trapped: prefer moves that have at least one onward in-bounds cell.
        onward = 0
        for ddx, ddy in moves:
            ex, ey = nx + ddx, ny + ddy
            if in_bounds(ex, ey):
                onward += 1
        score += 2.0 * onward

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best