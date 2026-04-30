def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def cell_free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if resources:
        # Choose the resource where we have the biggest deterministic "race advantage"
        best_r = None
        best_key = None
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; tie-break by absolute closeness.
            key = (od - sd, -sd)
            if best_key is None or key > best_key:
                best_key = key
                best_r = (rx, ry)

        rx, ry = best_r
        opp_to = man(ox, oy, rx, ry)
        # Evaluate moves by improving our distance to target and worsening opponent's.
        best_m = None
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not cell_free(nx, ny):
                continue
            sd = man(nx, ny, rx, ry)
            # Predict opponent effect: we can't move opponent, but we can still maximize their remaining advantage.
            # Reward moves that reduce sd strongly; penalize moves that let opponent be closer (od - sd becomes bigger for them).
            val = (opp_to - sd) * 20 - sd
            # Small bias: avoid moving directly into opponent direction while focusing on target.
            val -= man(nx, ny, ox, oy) // 3
            if best_val is None or val > best_val:
                best_val = val
                best_m = [dx, dy]
        if best_m is not None:
            return best_m
        return [0, 0]

    # No resources: maximize separation while staying safe
    best_m = [0, 0]
    best_d = -1
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_free(nx, ny):
            continue
        d = man(nx, ny, ox, oy)
        if d > best_d:
            best_d = d
            best_m = [dx, dy]
    return best_m