def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set((x, y) for x, y in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = [(dx, dy) for dx, dy in moves if dx != 0 or dy != 0] + [(0, 0)]

    # Use deterministic top resources near us to stay efficient, then score with advantage + denial.
    def topk_cells(k):
        arr = []
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            arr.append((d, rx, ry))
        arr.sort()
        return arr[:k]

    near = topk_cells(5 if len(resources) >= 5 else len(resources))

    best_score = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue

        my_best = -10**9
        denom = 0  # denial: how much this move worsens opponent for our near targets
        winish = 0  # count of targets where we are at least as close as opponent
        min_my_d = 10**9

        for d0, rx, ry in near:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            if opd <= myd:
                winish += 1
            if myd < min_my_d:
                min_my_d = myd
            # Denial prefers making opponent farther (positive when opd is large relative to myd)
            my_best = myd if my_best < myd else my_best
            denom += (opd - myd)
        # Prefer moves that strongly swing advantage on near targets, then quick collection, then denial
        score = (winish, denom, -min_my_d)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move