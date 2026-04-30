def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def value_for_target(myx, myy, rx, ry):
        md = dist(myx, myy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Want states where we are closer than opponent; also avoid extreme remoteness
        return (od - md) * 10 - md

    # If no visible resources, move to center-ish while avoiding obstacles and keeping away from opponent
    if not resources:
        targetx, targety = w // 2, h // 2
        bestd = 10**9
        best = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = dist(nx, ny, targetx, targety) * 2 + dist(nx, ny, ox, oy)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Choose move by maximizing best attainable "advantage" over all resources from the next position
    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = -10**18
        for rx, ry in resources:
            score = max(score, value_for_target(nx, ny, rx, ry))
        # Small tie-break: prefer keeping distance from opponent unless it sacrifices advantage
        score -= dist(nx, ny, ox, oy) * 0.1
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]