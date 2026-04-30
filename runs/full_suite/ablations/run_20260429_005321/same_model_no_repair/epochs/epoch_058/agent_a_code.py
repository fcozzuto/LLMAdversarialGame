def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe_cell(x, y):
        if (x, y) in obstacles:
            return False
        # Prefer cells not immediately adjacent to obstacles (reduce getting trapped)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    return False
        return True

    # Pick target that we can reach at least as fast as opponent; otherwise block by going for far contest.
    best_t = None
    best_score = -10**18
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    for tx, ty in resources:
        if (tx, ty) in obstacles:
            continue
        myd = dist(sx, sy, tx, ty)
        opd = dist(ox, oy, tx, ty)
        contest = 1 if myd <= opd else -1
        center = -((tx - cx) ** 2 + (ty - cy) ** 2)
        # Encourage closer and more central when contested; otherwise slightly prefer where we are relatively closer.
        score = (contest * 10000) - myd * 40 + (opd - myd) * 8 + center * 0.02
        if score > best_score:
            best_score = score
            best_t = (tx, ty)

    tx, ty = best_t
    # Greedy one-step: move to safe cell that minimizes distance to target, with tie-breaks vs opponent and obstacle proximity.
    best_move = [0, 0]
    best_mscore = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            if safe_cell(nx, ny):
                obstacle_pen = 0
            else:
                obstacle_pen = -50
            myd = dist(nx, ny, tx, ty)
            opd = dist(nx, ny, ox, oy)
            toward = -myd * 100
            avoid_opponent = (opd) * 0.5  # slight
            # Also discourage entering cells adjacent to obstacles even if safe_cell says false
            adj = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (nx + ax, ny + ay) in obstacles:
                        adj += 1
            mscore = toward + avoid_opponent + obstacle_pen - adj * 10
            if mscore > best_mscore:
                best_mscore = mscore
                best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]