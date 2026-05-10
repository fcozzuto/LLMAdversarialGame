def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            if inb(p[0], p[1]) and (p[0], p[1]) not in obstacles:
                unclaimed.append((p[0], p[1]))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    candidates = unclaimed
    if not candidates:
        candidates = [(x, y) for x in (0, w - 1) for y in range(h) if (x, y) not in obstacles] + \
                      [(x, y) for y in (0, h - 1) for x in range(w) if (x, y) not in obstacles]
        candidates = [c for c in candidates if inb(c[0], c[1])]
        if not candidates:
            return [0, 0]

    best_target = None
    best_val = None
    for tx, ty in candidates:
        ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        # Prefer grabbing far-from-opponent territory while not too far to reach.
        val = (do - 0.9 * ds)
        if best_val is None or val > best_val or (val == best_val and (ds, -do) < (best_ds, -best_do)):
            best_val = val
            best_target = (tx, ty)
            best_ds, best_do = ds, do

    tx, ty = best_target
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds_next = man(nx, ny, tx, ty)
        do_next = man(nx, ny, ox, oy)
        step_penalty = 0.02 * (dx == 0 and dy == 0)
        score = -ds_next + 0.55 * do_next - step_penalty
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]