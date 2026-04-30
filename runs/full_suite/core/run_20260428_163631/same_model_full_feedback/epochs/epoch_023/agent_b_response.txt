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
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    valid = [(dx, dy) for dx, dy in dirs if ok(sx + dx, sy + dy)]
    if not valid:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target choice: nearest resource; if none, go to center.
    if resources:
        resources_sorted = sorted(resources, key=lambda r: (md(sx, sy, r[0], r[1]), r[0], r[1]))
        tx, ty = resources_sorted[0]
    else:
        tx, ty = w // 2, h // 2

    # Evaluate moves: primary reduce distance to target; secondary avoid opponent; tertiary deterministic tie-break.
    best = None
    best_val = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        d_target = md(nx, ny, tx, ty)
        d_opp = md(nx, ny, ox, oy)
        # When chasing resources, don't step into opponent-adjacent squares.
        risk = 0
        if d_opp == 0:
            risk = 200
        elif d_opp == 1:
            risk = 40
        elif d_opp == 2:
            risk = 12
        # Mild preference to keep line toward opponent if resources are scarce (helps racing).
        steer = 0
        if not resources:
            steer = -md(nx, ny, ox, oy) * 0.5

        val = d_target * 10 + risk - steer + (nx * 0.01 + ny * 0.02)
        # Deterministic tie-break with fixed order from dirs.
        if best_val is None or val < best_val - 1e-9 or (abs(val - best_val) <= 1e-9 and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]