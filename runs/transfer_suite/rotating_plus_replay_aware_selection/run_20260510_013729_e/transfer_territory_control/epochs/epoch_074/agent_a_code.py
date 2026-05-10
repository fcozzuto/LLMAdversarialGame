def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_cell(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            return (x, y)
        return None

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        c = to_cell(p)
        if c is not None:
            x, y = c
            if 0 <= x < w and 0 <= y < h:
                obs.add(c)

    resources = observation.get("resources") or []
    targets = []
    for p in resources:
        c = to_cell(p)
        if c is not None:
            x, y = c
            if 0 <= x < w and 0 <= y < h:
                targets.append((x, y))
    if not targets:
        targets = [(w // 2, h // 2)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_t = targets[0]
    best_key = None
    for t in targets:
        key = (man((sx, sy), t), -man((ox, oy), t), t[0], t[1])
        if best_key is None or key < best_key:
            best_key = key
            best_t = t

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        score = man((nx, ny), best_t) - 0.1 * man((nx, ny), (ox, oy))
        key = (score, abs(dx) + abs(dy), dx, dy)
        if best_score is None or key < best_score:
            best_score = key
            best_move = [dx, dy]
    return best_move