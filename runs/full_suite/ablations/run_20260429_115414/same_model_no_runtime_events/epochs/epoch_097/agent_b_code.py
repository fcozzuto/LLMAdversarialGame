def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def step_score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        threat = cheb(nx, ny, ox, oy)
        if not resources:
            return threat
        best_res = 10**9
        on_res = 0
        for rx, ry in resources:
            if nx == rx and ny == ry:
                on_res = 1
                break
            d = cheb(nx, ny, rx, ry)
            if d < best_res:
                best_res = d
        if on_res:
            return 10**6 + 10 - threat
        return -best_res * 10 + threat

    bestv = -10**18
    bestmove = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            v = step_score(nx, ny)
            if v > bestv:
                bestv = v
                bestmove = (dx, dy)

    dx, dy = bestmove
    return [int(dx), int(dy)]