def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            obs.add((int(b[0]), int(b[1])))

    actions = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1), (0, 0), (0, 1),
               (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def min_cheb_to_obstacles(x, y):
        if not obs:
            return 10**9
        m = 10**9
        for bx, by in obs:
            cd = abs(x - bx) if abs(x - bx) > abs(y - by) else abs(y - by)
            if cd < m:
                m = cd
        return m

    # Predict next opponent step direction and move toward the intercept cell.
    step_x = 0 if ox == sx else (1 if ox > sx else -1)
    step_y = 0 if oy == sy else (1 if oy > sy else -1)
    tx, ty = ox - step_x, oy - step_y  # intercept slightly behind opponent relative to us
    if not valid(tx, ty):
        tx, ty = ox, oy
        if not valid(tx, ty):
            tx, ty = sx, sy

    best = None
    best_score = None
    # Deterministic tie-break: fixed action order as listed.
    for dx, dy in actions:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_target = dist2(nx, ny, tx, ty)
        d_opp = dist2(nx, ny, ox, oy)
        clear = min_cheb_to_obstacles(nx, ny)
        # Strongly prefer reducing opponent distance, but keep away from obstacles.
        score = d_opp * 100 + d_target + (1.0 / (clear + 1)) * 50
        if best_score is None or score < best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best