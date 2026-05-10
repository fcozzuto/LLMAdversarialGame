def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]
    obs = set((x, y) for x, y in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def next_pos(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            return sx, sy
        if (nx, ny) in obs:
            return sx, sy
        return nx, ny

    rem = observation.get("remaining_resource_count", len(resources))
    best = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        margin = do - ds  # positive => we arrive earlier
        if rem <= 4:
            key = (0 if margin >= 0 else 1, -margin, ds, rx, ry)
        else:
            key = (0 if margin >= 0 else 1, -margin if margin >= 0 else (ds - do), ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry, ds, do)
    _, tx, ty, _, _ = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = next_pos(dx, dy)
        dself = cheb(nx, ny, tx, ty)
        dopp = cheb(ox, oy, tx, ty)
        margin2 = dopp - dself
        # Prefer progress to target; then prefer improving lead; then avoid being led.
        score = (
            dself,
            0 if margin2 >= 0 else 1,
            -margin2,
            abs(nx - tx) + abs(ny - ty),
            abs(nx - ox) + abs(ny - oy),
            dx,
            dy,
        )
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]