def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick resource with best distance advantage (prefer ones we can reach sooner).
    best = None
    for r in resources:
        rx, ry = r
        d_self = dist((sx, sy), (rx, ry))
        d_opp = dist((ox, oy), (rx, ry))
        score = (d_opp - d_self, -rx, -ry)  # higher better, tie-break by position
        if best is None or score > best[0]:
            best = (score, (rx, ry))
    tx, ty = best[1] if best else (sx, sy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) == (sx, sy) and (tx, ty) != (sx, sy):
            # allow staying only if it can't move closer without hitting obstacles
            pass
        d_to = abs(nx - tx) + abs(ny - ty)
        d_op = abs(nx - ox) + abs(ny - oy)
        # Prefer closer to target, discourage getting too close to opponent (helps contest less)
        val = (-(d_to), d_op, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If all moves were blocked, stay.
    if best_val is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]