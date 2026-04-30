def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def dist(a, b):
        ax, ay = a; bx, by = b
        return max(abs(ax-bx), abs(ay-by))  # Chebyshev for 8-dir moves

    def target_from(pos):
        if not resources:
            return (W//2, H//2)
        best = None
        best_adv = None
        for r in resources:
            r = (r[0], r[1])
            myd = dist(pos, r)
            opd = dist((ox, oy), r)
            adv = (opd - myd)
            if best is None or adv > best_adv:
                best, best_adv = r, adv
            elif adv == best_adv:
                if dist(pos, r) < dist(pos, best):
                    best = r
                elif dist(pos, r) == dist(pos, best):
                    best = r if r < best else best
        return best

    # pick best target from current position
    target = target_from((sx, sy))

    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        blocked = (nx, ny) in obstacles
        myd = dist((nx, ny), target)
        opd = dist((ox, oy), target)
        # Prefer non-blocked; then minimize my distance; then maximize opponent disadvantage; then deterministic tie-break
        key = (blocked, myd, -(opd - myd), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    # If every move went out of bounds (unlikely), stay
    return [int(best_move[0]), int(best_move[1])]