def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    best = None
    best_score = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach first; otherwise strongly reduce opponent advantage.
        reach_first = 1 if myd <= opd else 0
        score = (reach_first * 1000) + (opd - myd) * 6 - myd
        # Small bias to avoid running past obstacles near the resource (local penalty).
        penalty = 0
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = rx + dx, ry + dy
            if (nx, ny) in obstacles:
                penalty += 2
        score -= penalty
        if best is None or score > best_score or (score == best_score and (myd, rx, ry) < best):
            best = (myd, rx, ry)
            best_score = score

    if best is None:
        return [0, 0]
    _, tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        # If opponent is currently closer to the target, prioritize breaking away while still progressing.
        opd2 = cheb(ox, oy, tx, ty)
        dist_to_opp = cheb(nx, ny, ox, oy)
        score = -myd2 * 10 + dist_to_opp * (2 if cheb(sx, sy, tx, ty) > opd2 else 1)
        if (nx, ny) == (tx, ty):
            score += 100000
        candidates.append((score, myd2, nx, ny, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    _, _, _, _, dx, dy = candidates[0]
    return [dx, dy]