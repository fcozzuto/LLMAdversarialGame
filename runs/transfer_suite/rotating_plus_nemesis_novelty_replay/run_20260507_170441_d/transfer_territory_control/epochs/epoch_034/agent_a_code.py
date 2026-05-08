def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res_list = []
    for r in resources:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res_list.append((x, y))
        except:
            pass

    if res_list:
        targets = res_list
    else:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        targets = [(cx, cy)]

    def dist_to_targets(nx, ny):
        best = None
        for tx, ty in targets:
            d = abs(nx - tx) + abs(ny - ty)
            if best is None or d < best:
                best = d
        return best

    best_move = (0, 0)
    best_score = None
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        d = dist_to_targets(nx, ny)
        score = d
        if best_score is None or score < best_score or (score == best_score and (dx, dy) > best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]