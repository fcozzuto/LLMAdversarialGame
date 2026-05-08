def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((x, y) for x, y in obstacles)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def pick_target():
        if not resources:
            return (w // 2, h // 2)
        best = None
        tx, ty = resources[0]
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - ds
            key = (margin, -ds, -(rx + ry), rx * 8 + ry)
            if best is None or key > best:
                best = key
                tx, ty = rx, ry
        return (tx, ty)

    tx, ty = pick_target()
    best_move = (10**9, 10**9, 0, 0)  # (score1, score2, dx, dy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        margin_after = do - ds

        # Also nudge toward any immediate resource if our chosen target changes next turn.
        immediate = 0
        for rx, ry in resources:
            if cheb(nx, ny, rx, ry) == 0:
                immediate = max(immediate, 1)
            elif cheb(nx, ny, rx, ry) == 1:
                immediate = max(immediate, 0)

        # Prefer positive margin, then closeness, then deterministically prefer lower dx/dy tie.
        score1 = -margin_after
        score2 = ds - immediate * 0.5
        key = (score1, score2, -dx, -dy)
        if key < (best_move[0], best_move[1], best_move[2], best_move[3]):
            best_move = (score1, score2, -dx, -dy)

    if best_move[2] == 0 and best_move[3] == 0:
        return [0, 0]
    return [-best_move[2], -best_move[3]]