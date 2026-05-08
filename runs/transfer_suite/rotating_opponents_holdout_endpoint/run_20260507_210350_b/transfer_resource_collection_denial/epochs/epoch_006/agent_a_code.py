def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    self_pos = (x, y)
    opp_pos = (ox, oy)

    if resources:
        best_r = None
        best_key = None
        for r in resources:
            if r in obstacles:
                continue
            ds = cheb(self_pos, r)
            do = cheb(opp_pos, r)
            margin = do - ds  # positive means we are closer
            # Prefer being closer first; tie-break on smaller ds, then stable coordinates
            key = (-1 if margin > 0 else 0, -margin, ds, r[0], r[1])
            if best_key is None or key < best_key:
                best_key, best_r = key, r
        target = best_r
    else:
        target = (w // 2, h // 2)

    tx, ty = target
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        ns = (nx, ny)
        ds = cheb(ns, target)
        do = cheb(opp_pos, target)
        # Primary: minimize our distance to target. Secondary: maximize our lead vs opponent.
        score = (ds, -(do - ds), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]