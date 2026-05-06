def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            t = (int(r[0]), int(r[1]))
            if t not in obstacles:
                resources.append(t)

    in_bounds = lambda x, y: 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        cx, cy = w // 2, h // 2
        dx = 0 if cx == sx else (1 if cx > sx else -1)
        dy = 0 if cy == sy else (1 if cy > sy else -1)
        return [dx, dy]

    def best_for_pos(px, py):
        best = -10**18
        for rx, ry in resources:
            selfd = abs(px - rx) + abs(py - ry)
            oppd = abs(ox - rx) + abs(oy - ry)
            # Out-approach opponent strongly; also prefer closer targets and slight anti-stall.
            val = (oppd - selfd) * 6 - selfd
            if selfd == 0:
                val += 1000
            best = max(best, val)
        return best

    # Evaluate each move by the best resource we can aim for from the next position.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        v = best_for_pos(nx, ny)

        # Extra tie-break: prefer moves that reduce our distance to the currently most contestable resource.
        # Contestable = where we are closest relative to opponent.
        contest_best = -10**18
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)
            score = (oppd - selfd) * 6 - selfd
            if score > contest_best:
                contest_best = score
        v += 0.25 * contest_best

        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]