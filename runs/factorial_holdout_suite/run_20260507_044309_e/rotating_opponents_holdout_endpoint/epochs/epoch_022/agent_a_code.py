def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    def dsq(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Pick a target resource where we are (ideally) closer than opponent.
    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dsq(sx, sy, rx, ry)
        od = dsq(ox, oy, rx, ry)
        adv = od - sd  # higher is better for us
        key = (-adv, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        sd = dsq(nx, ny, tx, ty)
        od = dsq(ox, oy, tx, ty)
        adv = od - sd

        # Mild opponent-avoidance: prefer staying away while advancing to target.
        oppd = dsq(nx, ny, ox, oy)
        # Score: primary = advantage, secondary = target closeness, tertiary = farther from opponent.
        score = (-(adv), sd, -oppd, dx, dy)

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]