def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    bestv = -10**9

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            min_dself = 10**9
            score = -cheb(nx, ny, ox, oy)  # keep pressure away
            for rx, ry in resources:
                dself = cheb(nx, ny, rx, ry)
                dop = cheb(ox, oy, rx, ry)
                if dself < min_dself:
                    min_dself = dself
                score += (dop - dself) * 3 - dself * 0.7
            # prefer moves that reduce distance to the best target
            score += 8.0 / (1 + min_dself)
            if score > bestv:
                bestv = score
                best = [dx, dy]
    else:
        # No visible resources: move to maximize distance from opponent while staying valid
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]

    return [int(best[0]), int(best[1])]