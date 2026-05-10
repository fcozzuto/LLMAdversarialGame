def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def king(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    # Pick a target that we can reach earlier, with preference for still-initialized games.
    # Use king distance because diagonal moves are allowed.
    best_r = None
    best_val = -10**18
    for rx, ry in resources:
        if not ok(rx, ry):
            continue
        sd = king(sx, sy, rx, ry)
        od = king(ox, oy, rx, ry)
        # Race: higher when we are closer than opponent.
        # Slightly prefer resources that are "more central" to reduce wandering.
        race = (od - sd) * 1000.0
        center = -abs(rx - cx) - abs(ry - cy)
        val = race + center - 0.1 * sd
        if val > best_val:
            best_val = val
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]

    rx, ry = best_r

    # Choose a legal move that most reduces our distance to the target; break ties by race advantage.
    best = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        sd2 = king(nx, ny, rx, ry)
        sd0 = king(sx, sy, rx, ry)
        progress = sd0 - sd2  # positive is good
        od = king(ox, oy, rx, ry)
        # Also consider how the move affects race outcome; reward being in front.
        race_after = (od - sd2) * 1000.0
        # Prefer moves that approach central area when progress is tied.
        center = -abs(nx - cx) - abs(ny - cy)
        score = progress * 1e6 + race_after + center - 0.01 * sd2
        if (best is None) or (score > best):
            best = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]