def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        m = 0
        for dx, dy in dirs:
            if valid(x + dx, y + dy):
                m += 1
        return m

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    tx, ty = ox, oy
    desired_dx, desired_dy = sign(tx - sx), sign(ty - sy)

    # Candidate ordering: try diagonal-to-target first, then single-axis, then rest.
    cand = []
    primary = (desired_dx, desired_dy)
    if primary in [(dx, dy) for dx, dy in dirs]:
        cand.append(primary)
    axis1 = (desired_dx, 0)
    axis2 = (0, desired_dy)
    if axis1 in [(dx, dy) for dx, dy in dirs]:
        cand.append(axis1)
    if axis2 in [(dx, dy) for dx, dy in dirs]:
        cand.append(axis2)
    for d in dirs:
        if d not in cand:
            cand.append(d)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    if not pursuer:
        tx, ty = far_corner[0], far_corner[1]

    best_d, best_score = (0, 0), None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, tx, ty)
        mob = mobility(nx, ny)
        # Obstacle-wall runner counter: prioritize reducing distance; for tie, prefer higher mobility (avoid getting stuck).
        score = dist - 0.05 * mob if pursuer else -dist + 0.05 * mob
        if best_score is None or (score < best_score if pursuer else score < best_score):
            best_score = score
            best_d = [dx, dy]

    if best_d is None:
        return [0, 0]
    return [int(best_d[0]), int(best_d[1])]