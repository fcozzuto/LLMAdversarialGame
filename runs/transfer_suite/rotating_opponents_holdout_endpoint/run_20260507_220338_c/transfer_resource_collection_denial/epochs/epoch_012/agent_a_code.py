def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        d = abs(x1 - x2) + abs(y1 - y2)
        return d

    if not resources:
        return [0, 0]

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        move_score = -10**18
        # Evaluate this move by the single best resource "race" it enables.
        for i, (rx, ry) in enumerate(resources):
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)

            # Big reward for landing directly on a resource.
            if nx == rx and ny == ry:
                score = 10**12 - i
            else:
                # Prefer being closer than opponent; then faster and earlier-index.
                score = (od - sd) * 1000 - sd * 5 - i
            if score > move_score:
                move_score = score

        # Tie-break: prefer moves that reduce y first, then x (more deterministic sweeping).
        if (move_score > best_score or
            (move_score == best_score and (ny, nx) < (best_move[1], best_move[0]))):
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]