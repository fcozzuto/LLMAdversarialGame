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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_after(nx, ny):
        if not resources:
            tx, ty = w // 2, h // 2
            d = cheb(nx, ny, tx, ty)
            return (1, d, 0)
        ccx, ccy = w // 2, h // 2
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            win_flag = 0 if ds < do else 1
            # Prefer winning resources; then closer ones; then deny ones opponent is close to.
            key = (win_flag, ds, -(do - ds), abs(rx - ccx) + abs(ry - ccy), rx, ry)
            if best is None or key < best:
                best = key
        return best

    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        key = best_after(nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move