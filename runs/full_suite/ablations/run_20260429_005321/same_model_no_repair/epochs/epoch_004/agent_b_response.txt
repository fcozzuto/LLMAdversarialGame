def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    def clamp_step(dx, dy):
        if dx < -1: dx = -1
        if dx > 1: dx = 1
        if dy < -1: dy = -1
        if dy > 1: dy = 1
        return dx, dy

    # Candidate deltas: 8-neighborhood + stay
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # Choose a target resource where we can "swing" access (opponent farther, we closer)
    target = None
    best = None
    for rx, ry in resources:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        swing = od - sd  # positive means we're closer than opponent
        # Also prefer resources that are not too far to ourselves
        key = (swing, -sd, -rx, -ry)
        if best is None or key > best:
            best = key
            target = (rx, ry)

    if target is None:
        tx, ty = (w // 2, h // 2)
    else:
        tx, ty = target

    # Greedy step: prefer reaching/closing to target, but avoid getting worse than opponent too often
    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sd_new = dist((nx, ny), (tx, ty))
        sd_cur = dist((sx, sy), (tx, ty))
        od_to_t = dist((ox, oy), (tx, ty))
        # Penalize moves that let opponent become more advantaged relative to us
        rel_new = od_to_t - sd_new
        rel_cur = od_to_t - sd_cur
        adv_delta = rel_new - rel_cur  # want <= 0 (not letting them gain advantage)
        # Tie-breakers for determinism
        key = (-sd_new, adv_delta, 0 if (dx, dy) == (0, 0) else 1, -nx, -ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]