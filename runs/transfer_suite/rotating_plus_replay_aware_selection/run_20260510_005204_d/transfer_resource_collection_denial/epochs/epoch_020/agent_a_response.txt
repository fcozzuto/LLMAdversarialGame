def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Choose best target by "who arrives first" plus minor center preference.
    best_t = resources[0]
    best_key = None
    cx0 = (w - 1) / 2.0
    cy0 = (h - 1) / 2.0
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        adv = opd - myd  # positive => we are closer
        center = -(abs(rx - cx0) + abs(ry - cy0))  # higher is better
        key = (adv, -myd, center, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    on_resource = set(tuple(p) for p in resources)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        myd0 = dist(sx, sy, tx, ty)
        myd1 = dist(nx, ny, tx, ty)
        opd0 = dist(ox, oy, tx, ty)
        opd1 = dist(ox, oy, tx, ty)  # opponent doesn't move this turn; keep deterministic

        step_gain = myd0 - myd1  # positive if closer
        hit = 1 if (nx, ny) in on_resource else 0

        # Encourage taking resources and improving our relative arrival.
        rel0 = opd0 - myd0
        rel1 = opd1 - myd1
        rel_gain = rel1 - rel0

        # Small tie-break: prefer moves that also move generally toward the target.
        toward = -dist(nx, ny, tx, ty)

        score = (hit * 10000) + (step_gain * 50) + (rel_gain * 200) + (toward)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move