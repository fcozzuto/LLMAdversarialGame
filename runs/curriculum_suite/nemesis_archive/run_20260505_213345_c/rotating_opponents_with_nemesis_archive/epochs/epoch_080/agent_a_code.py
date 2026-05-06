def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist8(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    # Counter "sweep_rows": avoid opponent's current row and prioritize resources where we beat them.
    best = None
    for r in resources:
        dm = dist8((sx, sy), r)
        do = dist8((ox, oy), r)
        row_avoid = 1 if r[1] != oy else 0
        # Strongly prefer resources not on opponent row; then prefer where we are closer.
        val = (do - dm, row_avoid, -dm, r[0], r[1])
        if best is None or val > best[0]:
            best = (val, r)

    target = best[1]
    dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
    dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)

    # If diagonal step would land on an obstacle, fall back to axis step deterministically.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Try x-only then y-only then stay.
        if (sx + dx, sy) not in obstacles:
            return [dx, 0]
        if (sx, sy + dy) not in obstacles:
            return [0, dy]
        return [0, 0]
    return [dx, dy]