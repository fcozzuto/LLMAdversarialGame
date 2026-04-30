def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    target = None
    if resources:
        best = None
        bestkey = None
        for rx, ry in resources:
            adv = dist(ox, oy, rx, ry) - dist(sx, sy, rx, ry)
            key = (-adv, dist(sx, sy, rx, ry), rx, ry)
            if bestkey is None or key < bestkey:
                bestkey = key
                best = (rx, ry)
        target = best

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if target:
            rx, ry = target
            d_self = dist(nx, ny, rx, ry)
            d_op = dist(ox, oy, rx, ry)
            cur_d_self = dist(sx, sy, rx, ry)
            race_gain = (cur_d_self - d_self) - 0.1 * (d_op - d_self)
            score = -d_self + 2.0 * race_gain + 0.001 * dist(nx, ny, ox, oy)
        else:
            score = -dist(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if valid(sx + best_move[0], sy + best_move[1]) else [0, 0]