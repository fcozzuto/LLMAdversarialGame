def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Deterministic tie-break order: prefer moving diagonally toward target, else smallest delta.
    moves.sort(key=lambda t: (abs(t[0]) + abs(t[1]) == 1, t[0], t[1]))

    def cell_value(x, y):
        # Choose best resource by "lead" and also slight preference for our closeness.
        best = None
        for rx, ry in resources:
            sd = man(x, y, rx, ry)
            od = man(ox, oy, rx, ry)
            lead = od - sd
            # Slightly reduce staying too far from resources to avoid slow dithering.
            key = (lead, -sd, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        return best[0]

    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        k = cell_value(nx, ny)
        # Extra term: if we can reach the most "contested" resource sooner than opponent, prioritize it.
        # Contested meaning: max (od - sd) already; this term helps break ties consistently.
        contested = k[0]
        tie = (k, contested)
        if best_key is None or tie > best_key:
            best_key = tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]