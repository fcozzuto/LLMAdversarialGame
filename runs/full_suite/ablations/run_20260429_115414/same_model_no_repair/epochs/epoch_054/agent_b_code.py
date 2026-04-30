def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles_list = observation.get("obstacles", [])
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if not resources:
        return [0, 0]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose resource that we can reach sooner (maximize opponent distance - self distance)
    best_r = None
    best_key = None
    for r in resources:
        rx, ry = r
        sd = manh((sx, sy), (rx, ry))
        od = manh((ox, oy), (rx, ry))
        key = (od - sd, -sd, -abs(rx - sx) - abs(ry - sy), rx, ry)  # deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = None

    # Precompute small obstacle proximity penalty
    def obstacle_penalty(x, y):
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obstacles:
                    p += 0.6
        return p

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        sd_after = manh((nx, ny), (tx, ty))
        sd_now = manh((sx, sy), (tx, ty))
        od_after = manh((ox, oy), (tx, ty))
        adv = od_after - sd_after  # higher is better: opponent farther than we are to target

        # Avoid oscillation: prefer moves that reduce distance to target
        progress = (sd_now - sd_after)

        # Also avoid standing still unless it's beneficial
        stay_pen = 0.25 if (dx == 0 and dy == 0) else 0.0

        score = (adv, progress, -sd_after, -obstacle_penalty(nx, ny), -abs(dx) - abs(dy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]