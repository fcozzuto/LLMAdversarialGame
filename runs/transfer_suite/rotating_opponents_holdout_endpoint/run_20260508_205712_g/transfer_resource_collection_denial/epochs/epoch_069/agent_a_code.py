def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs_set = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            obs_set.add((int(o[0]), int(o[1])))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def cell_score(nx, ny):
        if (nx, ny) in obs_set or not inb(nx, ny):
            return -10**18
        if not resources:
            cx, cy = (W - 1) // 2, (H - 1) // 2
            return -man(nx, ny, cx, cy)

        best = -10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer landing on a resource immediately; then prefer resource we can reach sooner than opponent.
            if sd == 0:
                base = 10**12
            else:
                base = (od - sd) * 1000 - sd
            # Small center bias to stabilize movement when ties exist.
            cx, cy = (W - 1) // 2, (H - 1) // 2
            base -= 0.1 * man(nx, ny, cx, cy)
            if base > best:
                best = base
        return best

    bestv = -10**18
    bestm = (0, 0)
    # Deterministic tie-break by move order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        v = cell_score(nx, ny)
        if v > bestv:
            bestv = v
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]