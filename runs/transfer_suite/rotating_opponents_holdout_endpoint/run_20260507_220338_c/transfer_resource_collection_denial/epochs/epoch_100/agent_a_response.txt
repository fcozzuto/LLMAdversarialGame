def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    tr = int(observation.get("turns_remaining", 0))
    endgame = tr <= 10

    best = None
    best_t = (0, 0)
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; deny opponent by favoring those farther from them.
        # In endgame, strongly prioritize immediate reach.
        score = ds - (2.0 * do / (1 + (1 if endgame else 0))) * (-1)  # invert effect
        # Equivalent: smaller ds is better; larger do is better.
        # Rewrite deterministically:
        key = (ds, -do) if endgame else (ds - 0.5 * do, -do)
        if best is None or key < best:
            best = key
            best_t = (rx, ry)

    tx, ty = best_t

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
                nx, ny = sx, sy
                dx, dy = 0, 0
            # Choose move that minimizes distance to target; break ties by deterministic ordering.
            d = man(nx, ny, tx, ty)
            # Secondary: keep moving generally to avoid stalling unless needed.
            progress = abs(nx - sx) + abs(ny - sy)
            candidates.append((d, -progress, dx, dy))

    candidates.sort()
    return [int(candidates[0][2]), int(candidates[0][3])]