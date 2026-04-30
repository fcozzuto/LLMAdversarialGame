def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    w, h = observation["grid_width"], observation["grid_height"]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_score = None

    if not resources:
        # If no resources visible, move toward opponent corner by mirroring
        tx, ty = w - 1 - x, h - 1 - y
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            score = -d
            if best_score is None or score > best_score:
                best_score = score
                best = [dx, dy]
        return best if best is not None else [0, 0]

    # Choose target resource minimizing our distance; break ties with advantage over opponent
    def nearest_dist(px, py, targets):
        md = None
        for rx, ry in targets:
            d = abs(px - rx) + abs(py - ry)
            if md is None or d < md:
                md = d
        return md if md is not None else 10**9

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        d_me = nearest_dist(nx, ny, resources)
        d_op = abs(nx - ox) + abs(ny - oy)

        # Also compute whether we are closer to any resource than the opponent (contest pressure)
        op_near = nearest_dist(ox, oy, resources)
        # Favor states where we reduce the gap to best resource compared to opponent
        gap_improve = (op_near - d_me)

        # Slightly prefer staying away from opponent to avoid direct contest collapse
        score = (-d_me) + (0.15 * d_op) + (0.6 * gap_improve)

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]