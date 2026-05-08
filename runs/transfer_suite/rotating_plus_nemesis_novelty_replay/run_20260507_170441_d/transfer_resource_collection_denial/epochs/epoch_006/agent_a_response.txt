def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {tuple(p) for p in obstacles}

    cand = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obst_pen(x, y):
        if not obstacles:
            return 0
        md2 = 10**18
        for ax, ay in obstacles:
            t = d2(x, y, ax, ay)
            if t < md2:
                md2 = t
        if md2 == 10**18:
            return 0
        # Strong penalty near obstacles; still deterministic and cheap.
        return 1000 if md2 == 0 else 200 if md2 <= 1 else 60 if md2 <= 2 else 0

    if not resources:
        return [0, 0]

    # Choose a resource we can beat: prefer larger (op_dist - my_dist), then prefer lower my_dist.
    best = None
    bestv = -10**18
    for rx, ry in resources:
        myd = d2(sx, sy, rx, ry)
        opd = d2(ox, oy, rx, ry)
        race = opd - myd  # positive => we are closer
        v = race * 1000 - myd + (-rx * 1 - ry * 1)  # tiny deterministic tie-break
        # Slightly avoid resources near obstacles.
        v -= obst_pen(rx, ry) // 2
        if v > bestv:
            bestv = v
            best = (rx, ry)

    tx, ty = best
    cur_in_obst = (sx, sy) in obs
    best_move = [0, 0]
    best_score = 10**18

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        # Heuristic: move closer to target, keep away from obstacles, avoid oscillation by mild preference for non-stay.
        score = d2(nx, ny, tx, ty) + obst_pen(nx, ny)
        if (dx, dy) == (0, 0) and not cur_in_obst:
            score += 8
        if score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move