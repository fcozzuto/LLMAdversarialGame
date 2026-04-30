def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def metric(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # diagonal allowed

    def adj_obstacle_pen(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    p += 1
        return p

    # Pick target: maximize how much closer we are than opponent; then prefer closer targets
    best_t = None
    best_val = -10**18
    for tx, ty in resources:
        if (tx, ty) in obstacles:
            continue
        myd = metric((sx, sy), (tx, ty))
        opd = metric((ox, oy), (tx, ty))
        val = (opd - myd) * 10 - myd * 0.5 - adj_obstacle_pen(tx, ty) * 0.2
        if val > best_val or (val == best_val and (tx, ty) < best_t):
            best_val = val
            best_t = (tx, ty)

    tx, ty = best_t
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break order: already ordered deltas
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = metric((nx, ny), (tx, ty))
        opd = metric((ox, oy), (tx, ty))
        # Encourage closing on target; discourage positions where opponent is closer
        score = (opd - myd) * 12 - myd
        score -= adj_obstacle_pen(nx, ny) * 0.6
        # Small preference to collect if moving onto resource
        if (nx, ny) in resources:
            score += 50
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]