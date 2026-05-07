def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    my_pos = (sx, sy)
    op_pos = (ox, oy)

    target = None
    best = None
    # First try to "own" a resource; else deny the one opponent can take soonest.
    for rx, ry in resources:
        r = (rx, ry)
        dmy = dist(my_pos, r)
        dop = dist(op_pos, r)
        if dmy <= dop:
            key = (0, dmy, dop, (rx + ry) % 2, rx, ry)
        else:
            key = (1, dop, dmy, -dop + dmy, rx, ry)
        if best is None or key < best:
            best = key
            target = r

    tx, ty = target
    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Choose move that reduces distance to target, with deterministic tie-breaking.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sc = dist((nx, ny), target)
        # Prefer lower distance; then fewer steps lost relative to opponent; then deterministic.
        my_after = sc
        op_after = dist(op_pos, target)
        key = (my_after, op_after - my_after, (dx == 0 and dy == 0), abs(dx) + abs(dy), dx, dy)
        if best_score is None or key < best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]