def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def norm_pos(v):
        if isinstance(v, dict):
            if "position" in v and v["position"]:
                v = v["position"]
            else:
                if "x" in v and "y" in v:
                    return int(v["x"]), int(v["y"])
                return None
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return None

    obstacles = set()
    for item in observation.get("obstacles", []) or []:
        p = norm_pos(item)
        if p:
            x, y = p
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for item in observation.get("resources", []) or []:
        p = norm_pos(item)
        if p:
            x, y = p
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    target = None
    if resources:
        target = min(resources, key=lambda p: dist2((sx, sy), p))
    else:
        target = (ox, oy)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best = None
    best_sc = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sc = dist2((nx, ny), target)
        if (nx, ny) == (ox, oy):
            sc -= 10**9
        if best_sc is None or sc < best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]