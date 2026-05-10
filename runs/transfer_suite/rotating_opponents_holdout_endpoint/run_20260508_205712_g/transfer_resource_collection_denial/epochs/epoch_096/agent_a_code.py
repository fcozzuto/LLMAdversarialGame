def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        ax, ay, bx, by = a, b, c, d
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    deltas = sorted(deltas, key=lambda d: (0 if d == (0, 0) else 1, d[0], d[1]))

    # Pick a target resource that we can out-race (or deny least if we can't).
    scored = []
    for (rx, ry) in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Higher is better: positive means we are closer/equal than opponent.
        margin = do - ds
        # Tie-break: prefer nearer resources once margin is similar.
        scored.append((-(margin), ds, rx, ry))
    scored.sort()
    top = scored[: min(7, len(scored))]

    best_target = None
    best_rank = None
    for item in top:
        _, ds, rx, ry = item
        do = cheb(ox, oy, rx, ry)
        margin = do - ds
        # Make sure we actively move; if margin is negative, still choose least-bad.
        rank = (-margin, ds, rx, ry)
        if best_rank is None or rank < best_rank:
            best_rank = rank
            best_target = (rx, ry)

    tx, ty = best_target
    cur_d = cheb(sx, sy, tx, ty)

    # Move to neighbor that reduces distance most while not walking into obstacles.
    best_move = (0, 0)
    best_val = (-10**9, -10**9, -10**9)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        nd = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer strictly improving, then best out-race potential after the move.
        improve = cur_d - nd
        margin_after = do - nd
        val = (improve, margin_after, -nd)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]