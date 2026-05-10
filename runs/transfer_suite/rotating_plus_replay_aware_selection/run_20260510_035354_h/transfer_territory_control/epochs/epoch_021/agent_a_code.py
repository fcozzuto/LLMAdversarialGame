def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []
    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_set = {(x, y) for x, y in obstacles if inb(x, y)}
    my_set = {(x, y) for x, y in my_t if inb(x, y)}
    op_set = {(x, y) for x, y in op_t if inb(x, y)}
    un_set = {(x, y) for x, y in unclaimed if inb(x, y)}

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # If totally contained, drift toward center to avoid easy sweeps, but still deterministically.
    if not un_set and not op_set:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if ax == cx else (1 if ax < cx else -1)
        dy = 0 if ay == cy else (1 if ay < cy else -1)
        return [dx, dy]

    # Precompute target distances from current position for tie-breaking.
    # Limit work by using a few nearest samples if large.
    op_list = list(op_set)
    un_list = list(un_set)

    def min_manhattan_to(points, x, y):
        if not points:
            return 999
        best = 999
        for px, py in points:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
                if best == 0:
                    return 0
        return best

    best_move = (0, 0)
    best_val = -10**9

    for dx, dy in deltas:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            # Engine keeps us in place on invalid; treat as same cell.
            nx, ny = ax, ay

        if (nx, ny) in my_set:
            cell_val = 1.0
        elif (nx, ny) in op_set:
            cell_val = 6.0  # encourage immediate flips
        elif (nx, ny) in un_set:
            cell_val = 3.5  # expansion
        else:
            cell_val = 0.8  # safe/edge empty-ish

        # Encourage moving toward frontiers (unclaimed) and, if present, toward opponent territory.
        d_un = min_manhattan_to(un_list, nx, ny) if un_set else 999
        d_op = min_manhattan_to(op_list, nx, ny) if op_set else 999

        # Prefer opponent when close enough; otherwise prioritize unclaimed.
        opp_bias = 0.0
        if op_set:
            opp_bias = 2.2 if d_op == 0 else (2.2 / (1 + d_op))

        val = cell_val + (0.9 / (1 + d_un if un_set else 5)) + opp_bias

        # Deterministic tie-break: lexicographically smallest (dx,dy) among equal values.
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]