def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if resources:
        best = None
        for r in resources:
            rx, ry = r
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # Prefer resources closer to us and relatively farther from opponent
            score = ds - 0.9 * do
            if best is None or score < best[0] or (score == best[0] and ds < best[1]):
                best = (score, ds, (rx, ry))
        tx, ty = best[2]
        cur_d = dist((sx, sy), (tx, ty))
    else:
        # No resources: go to center-ish while staying safe
        tx, ty = (w // 2, h // 2)
        cur_d = dist((sx, sy), (tx, ty))

    # Pick move that minimizes distance to target, avoiding obstacles and bounds
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist((nx, ny), (tx, ty))
        # Break ties deterministically: prefer closer, then prefer not moving away, then smallest delta
        val = (d, -(cur_d - d), abs(dx) + abs(dy), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]