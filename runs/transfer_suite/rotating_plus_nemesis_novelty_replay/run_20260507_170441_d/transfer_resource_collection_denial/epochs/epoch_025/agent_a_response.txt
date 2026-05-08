def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(p[0], p[1]) for p in obstacles}
    res_set = {(p[0], p[1]) for p in resources}
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_val = None
    best_move = [0, 0]

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        hit = 1 if (nx, ny) in res_set else 0
        # Evaluate best "race" resource available from this next cell.
        max_margin = -10**9
        best_selfd = 10**9
        best_oppd = 10**9
        for rx, ry in resources:
            selfd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            margin = oppd - selfd
            # Prefer resources we can reach sooner by margin; otherwise closest to us.
            if margin > max_margin or (margin == max_margin and (selfd < best_selfd or (selfd == best_selfd and oppd < best_oppd))):
                max_margin = margin
                best_selfd = selfd
                best_oppd = oppd

        # Objective: hit immediate resource first, then maximize margin, then minimize our distance, then minimize opponent distance.
        val = (hit, max_margin, -best_selfd, -best_oppd)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]