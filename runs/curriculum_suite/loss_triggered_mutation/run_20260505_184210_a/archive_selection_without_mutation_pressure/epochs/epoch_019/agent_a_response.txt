def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    if not resources:
        tx = (w - 1) // 4 if ox > (w - 1) // 2 else (3 * (w - 1)) // 4
        ty = (h - 1) // 4 if oy > (h - 1) // 2 else (3 * (h - 1)) // 4
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, tx, ty)
            key = (d, dx, dy)
            if best is None or key < best:
                best = key
        return [best[1], best[2]]

    # Deterministic target evaluation: prefer resources we can reach sooner than opponent,
    # otherwise fight for resources where opponent is farthest behind.
    best_move = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_for_cell = None
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Higher is better: capture priority, plus small bias for staying nearer resources.
            score = 0
            if d_self == 0:
                score += 10000
            # If we are not worse than opponent, heavily prioritize.
            if d_self <= d_opp:
                score += 6000 - 200 * d_self
            else:
                # Opponent likely denies; still consider if opponent is much farther.
                score += 250 - 120 * (d_self - d_opp) - 5 * d_self
            # Encourage moving toward high-value targets deterministically.
            # Tie-break with coordinate ordering.
            coord_bias = -(rx * 8 + ry)
            key = (-score, coord_bias, d_self, d_opp, rx, ry)
            if best_for_cell is None or key < best_for_cell:
                best_for_cell = key
        # Choose move that maximizes best_for_cell (via its key ordering).
        if best_move is None or best_for_cell < best_move:
            best_move = best_for_cell
            best_dxdy = (dx, dy)

    return [best_dxdy[0], best_dxdy[1]]