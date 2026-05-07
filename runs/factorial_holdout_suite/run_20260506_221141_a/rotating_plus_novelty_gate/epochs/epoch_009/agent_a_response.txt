def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obstacles:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        ax, ay = (dx if dx >= 0 else -dx), (dy if dy >= 0 else -dy)
        return ax if ax > ay else ay

    if not resources:
        return [0, 0]

    best = None
    tr = int(observation.get("turns_remaining", 0) or 0)
    late = 1.0 if tr <= 8 else (0.0 if tr >= 20 else (20 - tr) / 12.0)
    for p in resources:
        tx, ty = int(p[0]), int(p[1])
        if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obs_set:
            continue
        md = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - md
        # Later in game: reduce risk by preferring closer targets even if not maximal advantage
        cand = (adv * (1.0 - 0.6 * late) + (-md) * (0.6 * late), -md, tx, ty)
        if best is None or cand > best[0]:
            best = (cand, tx, ty)
    if best is None:
        return [0, 0]
    _, tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_step = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs_set:
            continue
        # Score: get closer to target; also discourage moves that let opponent reach it earlier
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # If we stand on/approach resource, strongly prioritize reduction
        step = myd
        opp_change = opd - cheb(ox, oy, tx, ty)  # 0, but keep structure deterministic
        score = (-step * 3.0) + ((opd - myd) * 2.0) + (-(abs((nx - tx)) + abs((ny - ty))) * 0.05) + opp_change
        tie = (tx, ty, nx, ny)
        cand = (score, -myd, tie[0], tie[1], tie[2], tie[3])
        if best_score is None or cand > best_score:
            best_score = cand
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]