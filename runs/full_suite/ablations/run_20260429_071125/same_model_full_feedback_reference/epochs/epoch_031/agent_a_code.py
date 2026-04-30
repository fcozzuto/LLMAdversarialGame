def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    w = int(w)
    h = int(h)
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    if not inb(sx, sy):
        for dx, dy in deltas:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    target = None
    best = 10**9
    for x, y in resources:
        d = abs(sx - x) + abs(sy - y)
        if d < best:
            best = d
            target = (x, y)

    if target is None:
        tx, ty = ox, oy
    else:
        tx, ty = target

    # If opponent is closer to a resource, nudge toward the opposite direction (still deterministic)
    if resources:
        closest_ours = 10**9
        closest_theirs = 10**9
        for x, y in resources:
            d1 = abs(sx - x) + abs(sy - y)
            d2 = abs(ox - x) + abs(oy - y)
            if d1 < closest_ours:
                closest_ours = d1
            if d2 < closest_theirs:
                closest_theirs = d2
        if closest_theirs < closest_ours:
            tx, ty = ox + (ox - sx), oy + (oy - sy)

    dx = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    dy = 0
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    # Deterministic try order: prefer the greedy step, then other directions
    prefs = [(dx, dy)]
    if (dx, dy) != (0, 0):
        prefs.append((dx, 0))
        prefs.append((0, dy))
    prefs += [(a, b) for (a, b) in deltas if (a, b) not in prefs]

    for mx, my in prefs:
        nx, ny = sx + mx, sy + my
        if inb(nx, ny):
            return [int(mx), int(my)]

    # Last resort: any valid neighbor
    for mx, my in deltas:
        if inb(sx + mx, sy + my):
            return [int(mx), int(my)]
    return [0, 0]