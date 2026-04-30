def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
    else:
        bestT = None
        bestScore = -10**9
        for rx, ry in resources:
            myd = dist(sx, sy, rx, ry)
            opd = dist(ox, oy, rx, ry)
            # Prefer resources I can reach first; tie-break toward nearer
            sc = (opd - myd) * 10 - myd
            if sc > bestScore:
                bestScore = sc
                bestT = (rx, ry)
        tx, ty = bestT

    bestMove = (0, 0)
    bestVal = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # Move evaluation: how much we improve our winning chances on resources
        if resources:
            cur_best = -10**18
            for rx, ry in resources:
                myd = dist(nx, ny, rx, ry)
                opd = dist(ox, oy, rx, ry)
                # Reward getting closer to my target and being ahead of opponent
                sc = (opd - myd) * 10 - myd
                # Mild deterrent: avoid moving such that opponent is very close to the same resource
                sc -= 0.1 * dist(ox, oy, nx, ny)
                if sc > cur_best:
                    cur_best = sc
            val = cur_best
        else:
            val = -(dist(nx, ny, tx, ty))
        # Prefer shorter actual step when values tie
        val -= 0.01 * dist(sx, sy, nx, ny)
        if val > bestVal:
            bestVal = val
            bestMove = (dx, dy)

    return [int(bestMove[0]), int(bestMove[1])]