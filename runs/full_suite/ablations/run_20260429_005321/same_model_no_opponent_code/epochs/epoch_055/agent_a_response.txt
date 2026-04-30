def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles_list = observation.get("obstacles", [])
    obstacles = set((p[0], p[1]) for p in obstacles_list) if obstacles_list else set()

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    # Evaluate each move by how much it improves "getting closer than opponent" to some resource
    # score = max over resources of (d_opp - d_self_after). Avoid obstacles heavily.
    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        local_best = -10**18
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            val = d_opp - d_self
            if val > local_best:
                local_best = val

        # Tie-break deterministically using turn parity and move index
        score = local_best * 1000 + ((observation["turn_index"] + i) % 2)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]