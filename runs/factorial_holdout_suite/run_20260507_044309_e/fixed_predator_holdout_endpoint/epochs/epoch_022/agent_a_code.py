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

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = resources[0]
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer being ahead; then faster; then deterministic.
        key = (od - sd, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Also consider overall "attack potential" to avoid bad swings.
    def overall_potential(x, y):
        best_lead = -10**9
        best_sd = 10**9
        for rx, ry in resources:
            sd = man(x, y, rx, ry)
            od = man(ox, oy, rx, ry)
            lead = od - sd
            if lead > best_lead or (lead == best_lead and (sd < best_sd or (sd == best_sd and (rx, ry) > best))):
                best_lead = lead
                best_sd = sd
        return best_lead, -best_sd

    cur_pot = overall_potential(sx, sy)

    best_mv = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) == (sx, sy):
            nxt_pot = cur_pot
        else:
            nxt_pot = overall_potential(nx, ny)
        self_d = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        lead = opp_d - self_d
        # Higher lead is better; then closer to target; then prefer moves that improve potential.
        key = (lead, nxt_pot[0], nxt_pot[1], -self_d, -nx, -ny)
        if best_key is None or key > best_key:
            best_key = key
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]