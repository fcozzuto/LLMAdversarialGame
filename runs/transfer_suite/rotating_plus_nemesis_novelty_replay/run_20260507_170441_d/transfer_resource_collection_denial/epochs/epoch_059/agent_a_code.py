def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles if p is not None)

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    # Evaluate a move with a 1-step lookahead: pick the move that maximizes our lead on best reachable resource.
    best_move = (10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        # If we move into a resource immediately, prefer it strongly.
        immediate = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                immediate = 10000
                break

        # Choose best resource for us from next position, scored by (opponent_dist - my_dist).
        best_key = None
        for rx, ry in resources:
            my_d = dist8(nx, ny, rx, ry)
            op_d = dist8(ox, oy, rx, ry)
            lead = op_d - my_d
            # Prefer larger lead; then closer to finish; then deterministic tie-break.
            key = (-lead, my_d, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
        lead_score = -best_key[0]
        my_d = best_key[1]
        rx, ry = best_key[2], best_key[3]
        # Composite: maximize (immediate, lead, negative distance), tie-break by position.
        score = (-immediate, -lead_score, my_d, rx, ry)
        if score < best_move:
            best_move = score
            ret = (dx, dy)

    return [int(ret[0]), int(ret[1])]