def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = -10**18
    best_move = (0, 0)

    # Deterministically prefer moves that can reach a resource earlier than opponent,
    # then prefer shorter distance to that resource.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        move_best = -10**18
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # If we are strictly closer, large bonus; if we tie, mild bonus; if behind, penalty.
            lead = od - sd
            score = lead * 1000 - sd
            # Slight deterministic bias toward "central" coordinates to break ties.
            score += -(abs(rx - (W - 1) / 2) + abs(ry - (H - 1) / 2)) * 0.01
            if score > move_best:
                move_best = score

        if move_best > best_score:
            best_score = move_best
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]