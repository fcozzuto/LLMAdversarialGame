def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        # Deterministic fallback: go toward center while avoiding obstacles
        cx, cy = w // 2, h // 2
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = (md(nx, ny, cx, cy), md(nx, ny, 0, 0))
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick a target with strong self advantage; if none, pick a target that hurts opponent the most.
    best_cell = None
    best_key = None
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        lead = do - ds  # positive means we are closer
        # Also consider distance to reduce "chasing" too far ahead.
        # Key: prioritize lead, then our proximity.
        key = (lead, -ds, -do)
        if best_key is None or key > best_key:
            best_key = key
            best_cell = (rx, ry)

    rx, ry = best_cell
    # Ant-denial movement: choose neighbor that maximizes expected gain against opponent,
    # approximated by reducing our distance and increasing opponent distance to the target.
    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        ns = md(nx, ny, rx, ry)
        no = md(ox, oy, rx, ry)
        # no changes this turn for opponent; use it to keep policy consistent with target choice.
        # Penalize moves that don't improve our distance.
        imp = md(sx, sy, rx, ry) - ns
        # Secondary: when imp is small/negative, steer to reduce opponent's eventual reach by
        # preferring moves that put us on a line toward the target's direction.
        step_dir = (0 if rx == sx else (1 if rx > sx else -1), 0 if ry == sy else (1 if ry > sy else -1))
        align = (dx == step_dir[0] and dy == step_dir[1])
        v = (imp, -ns, 1 if align else 0)
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]