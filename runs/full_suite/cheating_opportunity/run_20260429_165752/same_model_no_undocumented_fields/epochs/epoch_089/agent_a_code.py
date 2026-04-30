def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    ti = int(observation.get("turn_index") or 0)
    if ti % 2:
        dirs = dirs[1:] + dirs[:1]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    target = None
    if resources:
        best = None
        bestd = 10**9
        for x, y in resources:
            d = dist(sx, sy, x, y)
            if d < bestd or (d == bestd and (x, y) < best):
                bestd = d
                best = (x, y)
        target = best

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if target is not None:
            score = -dist(nx, ny, target[0], target[1])
        else:
            score = -dist(nx, ny, ox, oy)

        # Prefer moves that don't step away from our target too much, and slight tie-break.
        if target is not None:
            if resources:
                score += 0.01 * (-dist(nx, ny, target[0], target[1]) - dist(sx, sy, target[0], target[1]))

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    if best_move == (0, 0) and valid(sx, sy):
        return [0, 0]

    if not valid(sx + best_move[0], sy + best_move[1]):
        for dx, dy in dirs:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    return [best_move[0], best_move[1]]