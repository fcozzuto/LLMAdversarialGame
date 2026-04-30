def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    rset = set()
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                rset.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def candidates():
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                yield dx, dy, nx, ny

    if resources:
        bestR = None
        bestD = 10**9
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if d < bestD:
                bestD = d
                bestR = (rx, ry)
            elif d == bestD:
                # tie: prefer resource closer to center
                dc = cheb(rx, ry, cx, cy)
                dbc = cheb(bestR[0], bestR[1], cx, cy)
                if dc < dbc:
                    bestR = (rx, ry)

        rx, ry = bestR
        bestScore = -10**18
        bestMove = (0, 0)
        for dx, dy, nx, ny in candidates():
            # Higher is better
            dist = cheb(nx, ny, rx, ry)
            onRes = 1 if (nx, ny) in rset else 0
            oppDist = cheb(nx, ny, ox, oy)
            centerBias = -cheb(nx, ny, cx, cy) * 0.05
            score = (onRes * 1000) - dist * 10 + oppDist * 0.2 + centerBias
            if score > bestScore:
                bestScore = score
                bestMove = (dx, dy)
            elif score == bestScore:
                # deterministic tie-break: lexicographic by dx, then dy (prefer smaller dx magnitude toward center)
                if (abs(dx), abs(dy), dx, dy) < (abs(bestMove[0]), abs(bestMove[1]), bestMove[0], bestMove[1]):
                    bestMove = (dx, dy)
        return [int(bestMove[0]), int(bestMove[1])]

    # No resources visible: drift toward center while avoiding opponent by slight penalty
    bestScore = -10**18
    bestMove = (0, 0)
    for dx, dy, nx, ny in candidates():
        distC = cheb(nx, ny, cx, cy)
        oppDist = cheb(nx, ny, ox, oy)
        score = -distC * 5 + oppDist * 0.05
        if score > bestScore:
            bestScore = score
            bestMove = (dx, dy)
        elif score == bestScore:
            if (abs(dx), abs(dy), dx, dy) < (abs(bestMove[0]), abs(bestMove[1]), bestMove[0], bestMove[1]):
                bestMove = (dx, dy)
    return [int(bestMove[0]), int(bestMove[1])]