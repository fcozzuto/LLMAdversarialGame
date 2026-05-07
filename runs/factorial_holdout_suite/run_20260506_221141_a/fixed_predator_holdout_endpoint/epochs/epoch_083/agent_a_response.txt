def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx, dy = a - c, b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # pick a target under this move that we can reach first; break ties by lead then closeness
        local_best = None
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            # if we're not earlier, penalize; also bias toward picking something we can get soon
            key = (0 if my_d < op_d else 1, my_d - op_d, my_d)
            if local_best is None or key < local_best:
                local_best = key
        # final preference: first arrive first; then maximize (op_d - my_d) for that best target; then faster
        # approximate with the stored key: (phase, leadneg, my_d)
        final_key = local_best
        if best_key is None or final_key < best_key:
            best_key = final_key
            best_move = [dx, dy]

    return best_move