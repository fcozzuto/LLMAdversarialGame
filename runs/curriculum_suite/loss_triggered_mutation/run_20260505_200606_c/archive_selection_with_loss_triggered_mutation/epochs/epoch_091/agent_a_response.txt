def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    # Prefer moves that reduce "catch-up cost" to a good resource while keeping safer positioning.
    best = None  # (score, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Base: keep some pressure on opponent (don’t drift too far away).
        opp_d = man(nx, ny, ox, oy)

        # Score over resources: pick the best one for us this move.
        best_res = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Lower is better: go for resources where we can arrive sooner relative to opponent.
            val = sd - (od // 2)

            # Mild tie-break: favor closer/denser area and avoid being at immediate dead-ends.
            if best_res is None or val < best_res:
                best_res = val

        # Safety term: penalize moving into cramped area near obstacles.
        adj = 0
        for ax, ay in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            tx, ty = nx + ax, ny + ay
            if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obs:
                adj += 1

        # Combine: strongest drive to best_res, plus slight desire to keep opponent farther.
        score = best_res * 10 + adj * 3 + opp_d * 0.1
        if best is None or score < best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]