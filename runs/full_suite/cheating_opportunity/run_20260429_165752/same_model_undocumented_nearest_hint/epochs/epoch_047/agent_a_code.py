def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        tx, ty = W // 2, H // 2
    else:
        # Pick a resource that we can reach earlier than opponent; otherwise deny them if possible.
        def cheb(ax, ay, bx, by):
            dx = ax - bx
            if dx < 0: dx = -dx
            dy = ay - by
            if dy < 0: dy = -dy
            return dx if dx > dy else dy

        best = None
        best_key = None
        for tx, ty in resources:
            dme = cheb(sx, sy, tx, ty)
            dom = cheb(ox, oy, tx, ty)
            # Key: strongly prefer winning race; then prioritize closer; then farther from opponent.
            race = dom - dme
            key = (-1 if race > 0 else 0, -(race if race > 0 else 0), dme, -dom, (tx + ty) & 1, tx, ty)
            if best_key is None or key < best_key:
                best_key, best = key, (tx, ty)
        tx, ty = best

    def blocked(x, y):
        return not (0 <= x < W and 0 <= y < H) or (x, y) in obstacles

    # Choose move that reduces distance to target while avoiding obstacles.
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)
    candidates = []
    # Prefer diagonal/higher progress first
    for dx, dy in [(dx0, dy0), (dx0, 0), (0, dy0), (dx0, -dy0), (-dx0, dy0), (0, 0)]:
        nx, ny = sx + dx, sy + dy
        if not blocked(nx, ny) and (dx or dy or (nx == sx and ny == sy)):
            candidates.append((dx, dy))
    # If diagonal/primary blocked, consider all legal moves by greedy distance.
    if not candidates:
        candidates = []
        dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not blocked(nx, ny):
                candidates.append((dx, dy))
        # Deterministic order by distance then lexicographic.
    def cheb2(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        val = (cheb2(nx, ny, tx, ty), cheb2(nx, ny, ox, oy), abs((tx - nx) - (ty - ny)), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move