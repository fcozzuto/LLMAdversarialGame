def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []
    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []

    my_set = {(x, y) for x, y in my_t if 0 <= x < w and 0 <= y < h}
    op_set = {(x, y) for x, y in op_t if 0 <= x < w and 0 <= y < h}
    un_set = {(x, y) for x, y in unclaimed if 0 <= x < w and 0 <= y < h}
    obs_set = {(x, y) for x, y in obstacles if 0 <= x < w and 0 <= y < h}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not un_set and not op_set:
        dx = 0 if ax == (w - 1) // 2 else (1 if ax < (w - 1) // 2 else -1)
        dy = 0 if ay == (h - 1) // 2 else (1 if ay < (h - 1) // 2 else -1)
        return [dx, dy]

    opp_points = list(op_set) if op_set else []
    best_move = (0, 0)
    best_score = -10**18
    # Deterministic tie-break: fixed order, and prefer lexicographically smaller delta after score.
    for dx, dy in deltas:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        target = (nx, ny)
        cap = 0
        if target in op_set:
            cap = 6  # flipping on entry is valuable
        elif target in un_set:
            cap = 2
        elif target in my_set:
            cap = 0
        else:
            cap = 0

        # Expansion: how many unclaimed cells would become adjacent to us after move
        adj_un = 0
        for ex, ey in neigh:
            px, py = nx + ex, ny + ey
            if inb(px, py) and (px, py) in un_set:
                adj_un += 1

        # Pressure: prefer being closer to opponent territory (when it exists)
        dist_op = 0
        if opp_points:
            # compute min Chebyshev distance
            best_d = 10**9
            for ox, oy in opp_points:
                d = max(abs(ox - nx), abs(oy - ny))
                if d < best_d:
                    best_d = d
            dist_op = -best_d

        # Small preference to avoid wasting moves staying still when a capture/expansion move exists
        waste = -1 if (dx == 0 and dy == 0) and (cap > 0 or adj_un > 0) else 0

        score = cap * 10 + adj_un * 3 + dist_op + waste + (nx * 0 + ny * 0)
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]