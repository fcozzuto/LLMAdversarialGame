def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = {(p[0], p[1]) for p in obs_list}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in valid:
            d = max(abs(nx - tx), abs(ny - ty))
            cand = (d, max(abs(nx - ox), abs(ny - oy)))
            if best is None or cand < best:
                best = cand
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = (0, 0)
    best_score = None
    for dx, dy, nx, ny in valid:
        # Score the next cell by the best advantage it gives for any resource.
        # Advantage = (opponent distance - my distance). Higher is better.
        best_adv = None
        best_self = None
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - sd
            key = (adv, -sd, od)  # maximize adv; then minimize sd; then maximize od (deny risk)
            if best_adv is None or key > (best_adv, best_self, 0):
                best_adv = adv
                best_self = sd
        # Prefer moves that also reduce my distance to the currently most favorable resource.
        # Add small term to avoid ties by moving away from opponent.
        opp_near = max(abs(nx - ox), abs(ny - oy))
        score = (best_adv, -best_self, opp_near)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]