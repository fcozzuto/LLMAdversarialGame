def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    oxp, oyp = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        min_self = 10**9
        min_opp_ahead = -10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(oxp, oyp, rx, ry)
            if ds < min_self:
                min_self = ds
            # Prefer resources where we are closer than the opponent
            diff = do - ds
            if diff > min_opp_ahead:
                min_opp_ahead = diff

        # Small penalty for being adjacent to obstacles
        adj_pen = 0
        for ax, ay in obstacles:
            if cheb(nx, ny, ax, ay) == 1:
                adj_pen += 1

        # If we can capture (same cell) ds==0 => huge
        score = (20 * min_opp_ahead) - (2 * min_self) - (3 * adj_pen)
        if nx == sx and ny == sy:
            score -= 0.25  # slight preference to move

        if best is None or score > best_score:
            best = [dx, dy]
            best_score = score
    if best is None:
        return [0, 0]
    return best