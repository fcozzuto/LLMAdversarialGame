def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    if not resources:
        dx, dy = (0, 0)
        best = None
        for mx in (-1, 0, 1):
            for my in (-1, 0, 1):
                if mx == 0 and my == 0:
                    pass
                nx, ny = sx + mx, sy + my
                if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                    continue
                dist = max(abs(nx - ox), abs(ny - oy))
                cand = (dist, mx, my)
                if best is None or cand < best:
                    best = cand
        return [best[1], best[2]] if best is not None else [0, 0]

    def cd(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev for 8-way

    best_res = None
    best_val = None
    for r in resources:
        ds = cd((sx, sy), r)
        do = cd((ox, oy), r)
        # Prefer resources we can reach no later; then minimize our distance;
        # also give slight penalty if opponent is much closer.
        val = (1 if do < ds else 0, ds - do, ds, r[0], r[1])
        if best_val is None or val < best_val:
            best_val, best_res = val, r
    tx, ty = best_res

    moves = [(mx, my) for mx in (-1, 0, 1) for my in (-1, 0, 1)]
    best_move = None
    best_score = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Score: distance to target, with extra penalty for moving away from nearest free tile
        dt = cd((nx, ny), (tx, ty))
        # Mild opponent pressure: discourage letting opponent get closer to the same target
        dop = cd((ox, oy), (tx, ty))
        dop_next = cd((ox, oy), (tx, ty))  # opponent will move; keep deterministic mild effect by current state only
        score = (dt, dop_next - dop, abs(mx) + abs(my), mx, my)
        if best_score is None or score < best_score:
            best_score, best_move = score, (mx, my)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]