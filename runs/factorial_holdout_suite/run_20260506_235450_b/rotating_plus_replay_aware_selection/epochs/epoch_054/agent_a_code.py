def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer or faster in race
        key = (adv, -ds, -(abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)))
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    cur_ds = cheb(sx, sy, tx, ty)
    best_move = None
    for dx, dy, nx, ny in legal:
        nds = cheb(nx, ny, tx, ty)
        # primary: reduce our distance; secondary: improve race advantage after move
        nadv = cheb(ox, oy, tx, ty) - nds
        key = (-(nds - cur_ds), nadv, -nds)
        if best_move is None or key > best_move[0] or (key == best_move[0] and (dx, dy) < best_move[1]):
            best_move = (key, (dx, dy))
    return list(best_move[1])