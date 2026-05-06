def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    # If no resources: move to a deterministic "interception" point
    if not resources:
        tx = (sx + ox) // 2
        ty = (sy + oy) // 2
        best = None
        best_key = None
        for dx, dy, nx, ny in valid:
            d_self = abs(nx - sx) + abs(ny - sy)
            d_mid = abs(nx - tx) + abs(ny - ty)
            key = (d_mid, d_self, abs(nx - ox) + abs(ny - oy))
            if best_key is None or key < best_key:
                best_key, best = key, (dx, dy)
        return [best[0], best[1]]

    # With resources: prefer moves that create a lead on a resource; otherwise minimize self distance
    best = None
    best_key = None
    for dx, dy, nx, ny in valid:
        best_r_val = None
        best_r_key = None
        for rx, ry in resources:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            lead = od - sd  # positive if we are closer than opponent
            # Primary: lead; Secondary: closer to resource; Tertiary: reduce opponent proximity to that cell
            r_key = (-lead, sd, abs(nx - ox) + abs(ny - oy), rx, ry)
            if best_r_key is None or r_key < best_r_key:
                best_r_key = r_key
                best_r_val = lead
        # Prefer stronger best lead; tie-break deterministically by overall desirability
        key = (best_r_key[0], best_r_key[1], best_r_key[2], dx, dy)
        if best_key is None or key < best_key:
            best_key, best = key, (dx, dy)
    return [best[0], best[1]]