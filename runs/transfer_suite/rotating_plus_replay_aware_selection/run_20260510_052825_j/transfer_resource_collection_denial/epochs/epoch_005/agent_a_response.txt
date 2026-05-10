def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # Score move by best resource after the move (greedy interception-like)
    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Prefer grabbing resources sooner than opponent, but also keep future optionality
        move_best = None
        for r in resources:
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # If we can take it quickly and/or deny opponent, value rises.
            val = (od - sd) * 2.0 + (10 - sd) * 0.05 - od * 0.02
            # Small tie-break to favor nearer self targets and farther opponent ones.
            key = (-(val), sd, od, rx, ry)
            if move_best is None or key < move_best:
                move_best = key

        if move_best is None:
            continue

        # Additional deterministic tie-break: avoid stepping adjacent to obstacles
        adj_pen = 0
        for adx, ady in deltas[0:5]:
            ax, ay = nx + adx, ny + ady
            if (ax, ay) in obstacles:
                adj_pen += 1

        final_key = (move_best[0], move_best[1], move_best[2] + adj_pen * 0.01, dx, dy)
        if best_key is None or final_key < best_key:
            best_key = final_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]