def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [(w // 2, h // 2)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def pick_target():
        best = None
        for x, y in resources:
            ds = man(sx, sy, x, y)
            do = man(ox, oy, x, y)
            # Prefer targets where opponent is farther than us; also break ties toward lower x+y.
            key = (do - ds, -ds, -(x + y), -x)
            if best is None or key > best[0]:
                best = (key, (x, y))
        return best[1]

    tx, ty = pick_target()

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        ds_new = man(nx, ny, tx, ty)
        do_new = man(ox, oy, tx, ty)
        # Detour/contest heuristic:
        # - maximize (opponent distance - our distance) after move
        # - minimize our distance to target
        # - discourage approaching opponent directly while still moving
        d_to_op_new = man(nx, ny, ox, oy)
        d_to_op_old = man(sx, sy, ox, oy)
        key = ((do_new - ds_new), -ds_new, d_to_op_new - d_to_op_old, -(nx + ny), -dx, -dy)
        candidates.append((key, [dx, dy]))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda z: z[0], reverse=True)
    return candidates[0][1]