def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    def safe_xy(pos):
        if not pos or len(pos) < 2:
            return (0, 0)
        try:
            return (int(pos[0]), int(pos[1]))
        except:
            return (0, 0)

    sx, sy = safe_xy(observation.get("self_position"))
    ox, oy = safe_xy(observation.get("opponent_position"))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            try:
                x, y = int(r[0]), int(r[1])
            except:
                continue
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    role = observation.get("opponent_role") or ""
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_val = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        my_min = 10**9
        opp_min = 10**9
        target_gap = -10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds < my_min:
                my_min = ds
                opp_min_for = do
            gap = do - ds  # positive means I'm closer than opponent
            if gap > target_gap:
                target_gap = gap
                opp_min_for = do

        # Prefer being closer to some resource; if opponent is a denier, prioritize larger gap
        val = -my_min * 10 + (-opp_min_for) * 1 + target_gap * (5 if role == "resource_denier" else 2)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]