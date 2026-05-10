def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    t = observation.get("turn_index", 0)

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if (t % 2) == 1:
        dirs = [d for d in dirs if d != (0, 0)] + [(0, 0)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if unclaimed:
        # Prefer grabbing cells far from opponent (likely center-claimer), while staying reasonably close to self.
        best_cell = None
        best_val = -10**18
        for ux, uy in unclaimed:
            ds = abs(ux - sx) + abs(uy - sy)
            do = abs(ux - ox) + abs(uy - oy)
            val = (-ds) + 0.35 * do
            if (ux, uy) == (sx, sy):
                val += 0.1
            if val > best_val:
                best_val = val
                best_cell = (ux, uy)
        tx, ty = best_cell
    else:
        # Fall back: head toward opponent's territory boundary / center tension.
        tx, ty = (w // 2, h // 2)

    base_d = abs(sx - ox) + abs(sy - oy)
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        score = 0
        if (nx, ny) in opp_t:
            score += 1200  # flipping
        if (nx, ny) in unclaimed:
            score += 60
        if (nx, ny) in self_t:
            score += 8

        # Choose direction toward our target while keeping pressure: avoid stepping into opponent far-ahead zones.
        d_to_target = abs(nx - tx) + abs(ny - ty)
        score += -2.2 * d_to_target

        d_to_opp = abs(nx - ox) + abs(ny - oy)
        score += 0.5 * (base_d - d_to_opp)  # slightly prefer getting closer to contest

        # Mild bias toward edges/corners to counter center-claimer.
        edge_bias = min(nx, ny, (w - 1 - nx), (h - 1 - ny))
        score += 0.3 * (3 - edge_bias)

        # Deterministic tie-break
        score += -0.001 * ((dx + 1) * 10 + (dy + 1))

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]