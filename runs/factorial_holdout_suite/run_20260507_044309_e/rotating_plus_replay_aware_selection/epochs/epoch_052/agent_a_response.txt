def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None  # (key, target)
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can take earlier; then closer; then further from opponent to reduce contest.
            key = (0 if ds < do else 1, -(do - ds), ds, -(abs(ox - rx) + abs(oy - ry)), rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        if best is None:
            tx, ty = w // 2, h // 2
        else:
            tx, ty = best[1]

    best_move = (0, 0)
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if best_d is None or d < best_d or (d == best_d and (dx, dy) == (0, 0)):
            best_d = d
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]