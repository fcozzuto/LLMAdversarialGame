def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    remaining = int(observation.get("remaining_resource_count") or 0)
    target = None
    if resources and remaining > 0:
        bestd = 10**9
        for x, y in resources:
            d = abs(x - sx) + abs(y - sy)
            if d < bestd:
                bestd = d
                target = (x, y)
    if target is None:
        target = (ox, oy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        d = abs(target[0] - nx) + abs(target[1] - ny)
        score = d
        if best is None or score < best_score:
            best = (dx, dy)
            best_score = score
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]