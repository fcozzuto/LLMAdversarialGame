def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    opp_pos = (ox, oy)
    best = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        sd = dist2((sx, sy), (rx, ry))
        od = dist2(opp_pos, (rx, ry))
        # Prefer resources likely first (self not far behind), else closest.
        priority = (0 if sd <= od else 1, sd - 0.2 * od)
        if best is None or priority < best[0]:
            best = (priority, (rx, ry))
    tx, ty = best[1]

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d = dist2((nx, ny), (tx, ty))
        # Add mild tie-break: keep away from opponent while approaching target.
        adv = dist2((nx, ny), opp_pos)
        score = (d, -adv)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    if best_score is None:
        return [0, 0]
    return best_move