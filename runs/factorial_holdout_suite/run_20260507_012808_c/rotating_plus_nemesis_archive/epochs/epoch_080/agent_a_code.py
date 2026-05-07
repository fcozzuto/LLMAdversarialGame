def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a resource where we have the best guaranteed race advantage (or closest if no advantage).
    scored = []
    for rx, ry in resources:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        margin = od - sd  # positive => we are closer
        tie = (rx, ry)
        scored.append((margin, -sd, tie, (rx, ry)))
    scored.sort(reverse=True)
    target = scored[0][3]

    # Choose the best immediate step toward the target that preserves race advantage.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None
    tx, ty = target
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        sd = dist((nx, ny), (tx, ty))
        od = dist((ox, oy), (tx, ty))
        margin = od - sd
        # Prefer: move that increases margin; then decreases our distance; then lexicographic determinism.
        val = (margin, -sd, (dx, dy))
        if best_val is None or val > best_val:
            best_val, best = val, (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]