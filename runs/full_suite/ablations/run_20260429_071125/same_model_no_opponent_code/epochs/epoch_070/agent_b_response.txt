def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    # Choose a target resource where we are relatively closer than the opponent (deterministic tiebreaks)
    if resources:
        best = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            margin = do - ds  # positive means we are closer
            key = (margin, -ds, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (w - 1 if sx < ox else 0), (h - 1 if sy < oy else 0)

    # Greedy one-step evaluation to change policy from "direct chase": avoid opponent-favored paths
    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (None, None)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Primary: approach chosen target; Secondary: keep away from opponent relative to target
        ds_t = man(nx, ny, tx, ty)
        ds = man(nx, ny, tx, ty)
        do = man(ox, oy, tx, ty)
        # Bonus for moving onto a resource cell now
        on_res = 1 if (nx, ny) in resources else 0
        # Small tie-breaking: prefer smaller total movement magnitude then toward target
        step_mag = abs(dx) + abs(dy)
        key = (on_res, -ds_t, (do - ds), -step_mag, -nx, -ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]