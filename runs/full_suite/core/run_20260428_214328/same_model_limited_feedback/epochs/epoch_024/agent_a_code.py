def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    dxs = [-1, 0, 1]
    dys = [-1, 0, 1]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose target resource: prefer close to self, far from opponent
    if resources:
        best = None
        best_score = None
        for r in resources:
            ds = dist((sx, sy), r)
            do = dist((ox, oy), r)
            # smaller is better; add slight bias toward actual closeness
            score = ds - 0.6 * do + 0.05 * ds * (1 if ds <= 2 else 0)
            if best_score is None or score < best_score:
                best_score = score
                best = r
        tx, ty = best
    else:
        # No resources: drift toward center while avoiding obstacles
        tx, ty = w // 2, h // 2

    # Candidate moves (including staying)
    candidates = []
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                candidates.append((dx, dy))

    if not candidates:
        return [0, 0]

    # Pick move minimizing distance to target; tie-break by maximizing distance from opponent
    best_move = candidates[0]
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        v = dist((nx, ny), (tx, ty))
        od = dist((nx, ny), (ox, oy))
        # lexicographic: smaller v, larger od, then smaller dx^2+dy^2 (keep stable)
        key = (v, -od, dx * dx + dy * dy)
        if best_val is None or key < best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]