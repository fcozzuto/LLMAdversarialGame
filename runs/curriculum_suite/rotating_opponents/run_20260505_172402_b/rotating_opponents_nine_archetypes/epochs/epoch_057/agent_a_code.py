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

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target():
        best = None
        for (rx, ry) in resources:
            sd = dist(sx, sy, rx, ry)
            od = dist(ox, oy, rx, ry)
            # maximize advantage; break ties by closer to self
            key = (od - sd, -sd, -dist(ox, oy, rx, rx))  # last term is constant-ish, keeps tuple shape
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        return best[1] if best else None

    if not resources:
        tx, ty = (w // 2), (h // 2)
        moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        bestk, bestm = None, (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                k = (-dist(nx, ny, tx, ty), dx == 0 and dy == 0)
                if bestk is None or k > bestk:
                    bestk, bestm = k, (dx, dy)
        return [bestm[0], bestm[1]]

    target = best_target()
    rx, ry = target
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    bestk, bestm = None, (0, 0)
    cur_sd = dist(sx, sy, rx, ry)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # prioritize gaining advantage vs opponent, then speed to resource, then avoid dithering
            adv = od - sd
            k = (adv, -sd, -(sd - cur_sd))
            if bestk is None or k > bestk:
                bestk, bestm = k, (dx, dy)
    return [int(bestm[0]), int(bestm[1])]