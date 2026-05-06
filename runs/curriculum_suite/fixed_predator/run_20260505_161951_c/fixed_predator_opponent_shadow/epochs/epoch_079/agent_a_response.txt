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
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        best_key = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = man(nx, ny, tx, ty)
            # tie-breaker: approach opponent less (safer cornering)
            key = (d, man(nx, ny, ox, oy), dx, dy)
            if best_key is None or key < best_key:
                best_key, best = key, (dx, dy)
        return [best[0], best[1]]

    # Choose target with preference to resources we can reach competitively vs opponent.
    # Also bias toward reducing our distance over time by considering next-step distances.
    best_overall = None
    best_key = None
    for tx, ty in resources:
        self_d = man(sx, sy, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        # If we are already closer, emphasize grabbing it; if we are behind, only go if still beatable.
        compete = self_d - 0.85 * opp_d
        # Prefer closer targets when compete is similar.
        key_target = (compete, self_d, man(ox, oy, tx, ty), tx, ty)
        if best_key is None or key_target < best_key:
            best_key = key_target
            best_overall = (tx, ty)

    tx, ty = best_overall
    # If opponent is much closer, switch to "block" by moving toward the line midpoint between us and opponent
    # relative to the target; otherwise go straight for the target.
    self_d = man(sx, sy, tx, ty)
    opp_d = man(ox, oy, tx, ty)
    block = (opp_d - self_d) > 2

    if block:
        bx, by = (sx + ox) // 2, (sy + oy) // 2
        ax, ay = bx, by
    else:
        ax, ay = tx, ty

    best = None
    best_step = None
    best_key = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        dA = man(nx, ny, ax, ay)
        # discourage stepping away from the chosen target too much; helps prevent loops/diversity stagnation
        dT = man(nx, ny, tx, ty)
        # discourage giving opponent an easier path to the same target
        opp_future = man(nx, ny, tx, ty) - 0.5 * man(ox, oy, tx, ty)
        key = (dA, dT, opp_future, abs(dx) + abs(dy), dx, dy)
        if best_key is None or key < best_key:
            best_key, best_step = key, (dx, dy)
    return [best_step[0], best_step[1]]