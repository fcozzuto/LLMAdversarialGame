def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if legal(x, y):
                res.append((x, y))

    moves = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    target = None
    bestd = 10**9
    for x, y in res:
        d = cheb(sx, sy, x, y)
        if d < bestd:
            bestd = d
            target = (x, y)

    if target is None:
        best_pos = None
        best_sc = -10**9
        cx, cy = (W - 1) // 2, (H - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            sc = -cheb(nx, ny, cx, cy) + 0.1 * cheb(nx, ny, ox, oy)
            if sc > best_sc:
                best_sc = sc
                best_pos = (dx, dy)
        return list(best_pos) if best_pos is not None else [0, 0]

    tx, ty = target
    best_move = None
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        val = -d
        if (nx, ny) == target:
            val += 1000
        opd = cheb(ox, oy, tx, ty)
        if cheb(nx, ny, tx, ty) <= opd and (nx, ny) != (ox, oy):
            val += 5
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]] if best_move is not None else [0, 0]