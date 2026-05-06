def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = (0, 0)
    best_val = -10**18
    # Deterministic tie-break priority: prefer staying aligned with y first, then x, then diagonals earlier.
    pref_order = {(0, 1): 0, (0, 0): 1, (1, 0): 2, (-1, 0): 3, (1, 1): 4, (-1, 1): 5, (1, -1): 6, (-1, -1): 7, (0, -1): 8}

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # If we are stuck against an obstacle wall, allow staying.
        val = 0
        local_best = -10**18

        for rx, ry in resources:
            opp_d = man(ox, oy, rx, ry)
            our_d = man(nx, ny, rx, ry)
            # Primary: maximize lead over opponent on the same resource.
            lead = (opp_d - our_d)

            # Secondary: strong pull toward correct row, weak pull toward correct column.
            row_gap = abs(ny - ry)
            col_gap = abs(nx - rx)
            row_bonus = 10 if row_gap == 0 else (6 if row_gap == 1 else (3 if row_gap == 2 else 0))
            col_bonus = 2 if col_gap == 0 else (1 if col_gap == 1 else 0)

            # Tertiary: slight preference to move away from opponent when close to current best row.
            opp_close = man(nx, ny, ox, oy)
            sep_pen = -3 if opp_close <= 2 and row_gap == 0 else 0

            # Slight "interception": if we move onto same row/col trend as opponent toward this resource.
            our_to_res = man(nx, ny, rx, ry)
            opp_to_res = man(ox, oy, rx, ry)
            intercept = 4 if (our_to_res <= opp_to_res and (ny == ry or nx == rx)) else 0

            # Weighted score for this resource.
            s = lead * 3 + row_bonus + col_bonus + sep_pen + intercept

            if s > local_best:
                local_best = s

        val = local_best

        # Ensure deterministic tie-break.
        if val > best_val or (val == best_val and pref_order[(dx, dy)] < pref_order[best]):
            best_val = val
            best = (dx, dy)

    # Fallback: if somehow all moves invalid, stay.
    if best not in [(dx, dy) for dx, dy in moves]:
        return [0, 0]
    return [best[0], best[1]]