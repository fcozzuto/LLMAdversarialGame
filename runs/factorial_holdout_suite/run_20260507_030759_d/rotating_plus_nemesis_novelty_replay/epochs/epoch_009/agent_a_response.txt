def choose_move(observation):
    def xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return 0, 0

    def inb(x, y, w, h):
        return 0 <= x < w and 0 <= y < h

    def steps(a, b):
        ax, ay = a
        bx, by = b
        dx = abs(bx - ax)
        dy = abs(by - ay)
        return dx if dx > dy else dy  # Chebyshev since diagonals allowed

    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = xy(observation.get("self_position", [0, 0]))
    ox, oy = xy(observation.get("opponent_position", [7, 7]))
    resources = [xy(r) for r in (observation.get("resources", []) or [])]
    obstacles = set(xy(o) for o in (observation.get("obstacles", []) or []))

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    if not resources:
        # move toward opponent corner to reduce denier options when no resources
        tx, ty = (0, 0) if (sx + sy) > (ox + oy) else (7, 7)
        best = None
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny, w, h) or (nx, ny) in obstacles:
                continue
            v = -((tx - nx) ** 2 + (ty - ny) ** 2)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    my = (sx, sy)
    opp = (ox, oy)

    # Target selection: prefer resources I can reach significantly earlier; avoid "denied" resources
    best_t = None
    best_key = None
    for r in resources:
        myd = steps(my, r)
        oppd = steps(opp, r)
        # If opponent can grab almost immediately and I'm far, deprioritize
        if oppd <= 1 and myd > oppd:
            continue
        key = (oppd - myd, -myd)  # maximize advantage, then closer
        if best_key is None or key > best_key:
            best_key = key
            best_t = r

    if best_t is None:
        best_t = min(resources, key=lambda r: steps(my, r))

    tx, ty = best_t

    # Move choice: greedily reduce my distance to target while maintaining/expanding advantage
    best = [0, 0]
    bestk = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny, w, h) or (nx, ny) in obstacles:
            continue
        new_my = (nx, ny)
        if (nx, ny) == (tx, ty):
            k = (10**6, 10**6)  # immediate collection
        else:
            myd = steps(new_my, (tx, ty))
            oppd = steps(opp, (tx, ty))
            k = (oppd - myd, -myd)  # maximize my lead / minimize my remaining
        if bestk is None or k > bestk:
            bestk = k
            best = [dx, dy]

    return [int(best[0]), int(best[1])]