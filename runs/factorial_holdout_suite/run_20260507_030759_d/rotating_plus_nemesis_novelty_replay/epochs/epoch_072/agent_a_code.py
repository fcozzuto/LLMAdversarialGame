def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Pick best reachable resource by deterministic score: maximize advantage; then prefer closer.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        advantage = do - ds  # higher => we can arrive earlier
        # Small bias to avoid resources that are "too close" to opponent already
        if best_key is None or (advantage, -ds, -rx - ry) > best_key:
            best_key = (advantage, -ds, -rx - ry)
            best = (rx, ry)

    tx, ty = best
    if sx == tx and sy == ty:
        return [0, 0]

    # Choose one-step move that reduces distance to target; keep safe and also keep/improve relative advantage.
    best_move = [0, 0]
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nds = cheb(nx, ny, tx, ty)
        # Compute relative advantage after the move
        nadv = cheb(ox, oy, tx, ty) - nds
        # Prefer reducing target distance; then improve advantage; then move that stays away from edges slightly.
        key = (-nds, nadv, abs((nx - (w - 1) / 2)) + abs((ny - (h - 1) / 2)))
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]