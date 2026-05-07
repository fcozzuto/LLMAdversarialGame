def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = {tuple(p) for p in obs_list}
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestv:
                bestv = d
                best = [dx, dy]
        return best

    res = [tuple(r) for r in resources]
    best_move = [0, 0]
    best_score = -10**18
    for mdx, mdy in dirs:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue
        # Choose the resource that gives us the best "win" margin from this next step
        best_margin_for_move = -10**18
        best_ds = 10**9
        for rx, ry in res:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = (do - ds)  # positive means we are closer than opponent (or at least not worse)
            if margin > best_margin_for_move or (margin == best_margin_for_move and ds < best_ds):
                best_margin_for_move = margin
                best_ds = ds
        # Encourage immediate collection (exact landing) and denier avoidance
        win_bonus = 3 if (nx, ny) in obstacles else 0  # obstacles shouldn't be valid anyway
        collect_bonus = 4 if (nx, ny) in res else 0
        score = (best_margin_for_move * 10) + collect_bonus - best_ds + win_bonus
        if score > best_score:
            best_score = score
            best_move = [mdx, mdy]

    return best_move