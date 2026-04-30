def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    if not resources:
        return [0, 0]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    best = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        d = dist2((sx, sy), (rx, ry)) - 0.25 * dist2((ox, oy), (rx, ry))
        if best is None or d < best[0]:
            best = (d, rx, ry)
    if best is None:
        return [0, 0]
    _, tx, ty = best

    dx = 0
    dy = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    moves = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (-dx, 0), (0, -dy), (0, 0)]
    candidates = []
    for mdx, mdy in moves:
        nx = sx + mdx
        ny = sy + mdy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        candidates.append((nx, ny, mdx, mdy))

    if not candidates:
        return [0, 0]

    # Score candidates: closer to target; avoid getting too close to opponent unless beneficial.
    bestc = None
    for nx, ny, mdx, mdy in candidates:
        c = dist2((nx, ny), (tx, ty)) + 0.35 * dist2((nx, ny), (ox, oy))
        if bestc is None or c < bestc[0]:
            bestc = (c, mdx, mdy)
    return [int(bestc[1]), int(bestc[2])]