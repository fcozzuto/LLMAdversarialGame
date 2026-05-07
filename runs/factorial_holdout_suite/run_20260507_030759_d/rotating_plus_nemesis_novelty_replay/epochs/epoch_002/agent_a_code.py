def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    res = observation.get("resources", []) or []
    obst = observation.get("obstacles", []) or []
    obstacles = set((x, y) for x, y in obst)

    env = observation.get("environment_name", "resource_collection")

    if env != "resource_collection":
        # Simple fallback: head toward closest visible resource if any, else toward opponent.
        if res:
            rx, ry = min(res, key=lambda p: abs(p[0]-sx)+abs(p[1]-sy))
            dx = 0 if rx == sx else (1 if rx > sx else -1)
            dy = 0 if ry == sy else (1 if ry > sy else -1)
            return [dx, dy]
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    if not res:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def md(x1, y1, x2, y2):  # Manhattan distance
        return abs(x1 - x2) + abs(y1 - y2)

    best_target = None
    for rx, ry in res:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # Prefer targets we can reach no later than opponent; otherwise, prefer those with smallest (sd-od)
        if sd <= od:
            key = (0, sd, -od, rx, ry)
        else:
            key = (1, sd - od, sd, rx, ry)
        if best_target is None or key < best_target[0]:
            best_target = (key, (rx, ry))
    tx, ty = best_target[1]

    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = md(nx, ny, tx, ty)
        # Tie-break deterministically: smaller nd, then lexicographic move
        key = (nd, nx, ny, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, [dx, dy])

    if best_move is None:
        return [0, 0]
    return best_move[1]