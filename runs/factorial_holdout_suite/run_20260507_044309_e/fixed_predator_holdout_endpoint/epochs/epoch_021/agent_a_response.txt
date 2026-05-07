def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a resource where we arrive earlier than the denier, else the best swing.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        lead = od - sd  # positive means we are closer
        # Prefer larger lead; tie-break by smaller sd (faster), then deterministic coord order.
        key = (lead, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Choose next step that heads to target, but also discourages opponent from improving.
    best_mv = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        self_d = man(nx, ny, tx, ty)
        opp_d_to_tx = man(ox, oy, tx, ty)
        # Estimate opponent "denial pressure": how much closer they'd be if they moved optimally
        # toward the same target in one step (approx via best neighbor distance).
        min_opp = None
        for pdx, pdy in dirs:
            px, py = ox + pdx, oy + pdy
            if not inside(px, py) or (px, py) in obstacles:
                continue
            d = man(px, py, tx, ty)
            if min_opp is None or d < min_opp:
                min_opp = d
        if min_opp is None:
            min_opp = opp_d_to_tx

        # Prefer smaller self distance; then prefer making the opponent's next distance large.
        score = (-self_d, min_opp, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]