def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    target = None
    if resources:
        best = None
        for x, y in resources:
            d = abs(x - sx) + abs(y - sy)
            if best is None or d < best[0]:
                best = (d, x, y)
        target = (best[1], best[2]) if best else None

    if target is None:
        target = (w // 2, h // 2)

    dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        if (nx, ny) == (ox, oy):
            score = -10**9
        else:
            dist = abs(nx - target[0]) + abs(ny - target[1])
            opp_push = abs(nx - ox) + abs(ny - oy)
            score = (-dist) + (0.1 * opp_push)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_score is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                return [dx, dy]
        return [0, 0]

    return [best_move[0], best_move[1]]