def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])

    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs_set.add((p[0], p[1]))

    def dist_cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    best = None
    # Prefer resources we can reach earlier than opponent; deterministic tie-break by coord sum then x,y.
    for rx, ry in resources:
        if not in_bounds(rx, ry):
            continue
        myd = dist_cheb(sx, sy, rx, ry)
        opd = dist_cheb(ox, oy, rx, ry)
        # Lower is better: want myd < opd. Add tiny bias toward fewer steps and toward center-ish.
        center_bias = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
        val = (myd - 0.65 * opd) + 0.01 * myd + 0.001 * center_bias
        key = (val, myd, -opd, rx + ry, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    target = best[1]
    tx, ty = target

    # Candidate moves: fixed order for determinism
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Prefer moves that reduce distance to target; avoid obstacles; prefer closer to target then to prevent giving opponent advantage
    cur_my = dist_cheb(sx, sy, tx, ty)
    cur_opd = dist_cheb(ox, oy, tx, ty)

    best_move = (10**9, 10**9, 10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue
        myd = dist_cheb(nx, ny, tx, ty)
        opd = dist_cheb(ox, oy, tx, ty)
        # Value: prioritize reaching sooner; break ties by increasing lead (opponent farther), then lexicographic delta.
        score = (myd - 0.65 * opd, myd, -(opd), dx, dy)
        if score < (best_move[0], best_move[1], best_move[2], best_move[3], best_move[4]):
            best_move = (score[0], score[1], score[2], score[3], score[4])

    if best_move[3] == 0 and best_move[4] == 0:
        # If staying is chosen but moving to a free adjacent cell could still reduce distance, take best reduction move.
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obs_set:
                myd = dist_cheb(nx, ny, tx, ty)
                if myd < cur_my:
                    return [dx, dy]
    return [best_move[3], best_move[4]]