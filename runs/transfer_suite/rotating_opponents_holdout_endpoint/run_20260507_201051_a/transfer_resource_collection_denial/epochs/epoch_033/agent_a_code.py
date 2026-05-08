def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def norm_pos(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                return (x, y)
        return None

    s = norm_pos(observation.get("self_position")) or (0, 0)
    o = norm_pos(observation.get("opponent_position")) or (w - 1, h - 1)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        c = norm_pos(p)
        if c is not None:
            obstacles.add(c)

    resources = []
    for p in observation.get("resources") or []:
        c = norm_pos(p)
        if c is not None and c not in obstacles:
            resources.append(c)

    if not resources:
        dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in dirs:
            nx, ny = s[0] + dx, s[1] + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target = resources[0]
    bestd = man(s, target)
    for r in resources[1:]:
        d = man(s, r)
        if d < bestd:
            bestd, target = d, r

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = s[0] + dx, s[1] + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        ns = (nx, ny)
        key = (man(ns, target), -man(ns, o), 0 if ns == target else 1)
        if best_key is None or key < best_key:
            best_key, best = key, [dx, dy]
    return best if best is not None else [0, 0]