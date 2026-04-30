def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    if not resources:
        return [0, 0]

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    def inb(p):
        return 0 <= p[0] < w and 0 <= p[1] < h

    # Choose a target resource where we are relatively closer than the opponent (deterministic).
    best_r = None
    best_key = None
    for r in resources:
        rx, ry = r[0], r[1]
        if (rx, ry) in obstacles:
            continue
        ds = dist((x, y), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        key = (ds - do, ds + 0.001 * (rx + ry), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)
    if best_r is None:
        return [0, 0]

    tx, ty = best_r
    best_move = [0, 0]
    best_score = None

    # Evaluate 9 deterministic candidate moves; diagonal allowed.
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if not inb((nx, ny)):
                continue
            if (nx, ny) in obstacles:
                score = -1e9
            else:
                d_self = dist((nx, ny), (tx, ty))
                d_opp = dist((ox, oy), (tx, ty))
                # Prefer getting closer to our target, and avoid letting opponent get closer too.
                # Also bias slightly toward moving away from opponent to reduce immediate contest.
                away = dist((nx, ny), (ox, oy))
                score = (-d_self) + 0.35 * (d_opp - d_self) + 0.05 * away - 0.01 * (abs(dx) + abs(dy))
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]