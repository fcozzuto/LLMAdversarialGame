def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    occ = obstacles

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Pick a resource: prefer ones where we are relatively closer than opponent.
    target = None
    best = None
    if resources:
        for r in resources:
            sd = dist((sx, sy), r)
            od = dist((ox, oy), r)
            score = (od - sd) - 0.05 * sd  # primarily deny opponent, then be efficient
            if best is None or score > best:
                best = score
                target = r
        # If everything favors opponent too much, fall back to nearest resource.
        if best is not None and best < 0:
            target = min(resources, key=lambda r: dist((sx, sy), r))

    # If no resources, drift to center while keeping distance from opponent.
    if target is None:
        tx, ty = (w - 1) / 2, (h - 1) / 2
        target = (tx, ty)

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in occ:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    targetx, targety = target
    best_move = legal[0]
    best_val = None
    for dx, dy, nx, ny in legal:
        dself = dist((nx, ny), (targetx, targety))
        dopp = dist((nx, ny), (ox, oy))
        on_resource = 1.0 if any((nx == rx and ny == ry) for rx, ry in resources) else 0.0
        # Maximize: go to target, keep away from opponent, grab if on resource.
        val = (-dself) + 0.12 * dopp + 3.0 * on_resource
        # Tie-break deterministically: prefer staying if equally good, then smallest dx, then smallest dy.
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]