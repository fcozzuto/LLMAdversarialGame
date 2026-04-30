def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        return [0, 0]

    # Pick a target that is more "winnable": we want to become closer than opponent, but also avoid easy opponent denial.
    best_t = None
    best_key = None
    for r in resources:
        rx, ry = r[0], r[1]
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Higher is better: (od - sd). Tie-break: prefer larger od (harder for opponent), then smaller sd (closer for us).
        key = (od - sd, od, -sd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                moves.append((dx, dy))

    def near_obstacle_pen(x, y):
        # Penalize being adjacent to obstacles to avoid getting boxed in.
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    return 0.25
        return 0.0

    best_move = (0, 0)
    best_score = None
    cur_sd = dist((sx, sy), (tx, ty))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            continue
        sd = dist((nx, ny), (tx, ty))
        od = dist((ox, oy), (tx, ty))
        # Score favors becoming closer to target than opponent (od - sd), and reducing our own distance.
        # Also discourages stalling unless already at the target.
        stall_pen = 0.0
        if dx == 0 and dy == 0 and cur_sd != 0:
            stall_pen = 1.0
        progress_bonus = (cur_sd - sd)  # positive if we move closer
        score = (od - sd) + 0.15 * progress_bonus - 0.06 * sd - near_obstacle_pen(nx, ny) - stall_pen
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]