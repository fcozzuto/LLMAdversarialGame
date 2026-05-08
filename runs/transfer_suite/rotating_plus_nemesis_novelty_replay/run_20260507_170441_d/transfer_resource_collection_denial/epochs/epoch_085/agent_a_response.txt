def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles if p is not None and len(p) >= 2)

    if not resources:
        return [0, 0]

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Deny choice: contest a resource the opponent is at most slightly closer to; otherwise grab our nearest.
    contest = []
    for rx, ry in resources:
        my_d = dist_cheb(sx, sy, rx, ry)
        op_d = dist_cheb(ox, oy, rx, ry)
        if op_d - my_d <= 1:
            contest.append((op_d, my_d, rx, ry))
    if contest:
        contest.sort()
        _, _, tx, ty = contest[0]
    else:
        best = None
        for rx, ry in resources:
            my_d = dist_cheb(sx, sy, rx, ry)
            key = (my_d, dist_cheb(ox, oy, rx, ry), rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    # Choose move that most reduces our distance to target, while also increasing opponent distance to it.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        my_d = dist_cheb(nx, ny, tx, ty)
        op_d = dist_cheb(ox, oy, tx, ty)  # opponent position static for our decision
        score = my_d * 10 - op_d * 3 + abs(dx) + abs(dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]