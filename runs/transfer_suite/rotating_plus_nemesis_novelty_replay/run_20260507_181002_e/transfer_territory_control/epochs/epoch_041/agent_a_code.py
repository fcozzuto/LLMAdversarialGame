def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**18, 0, 0)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # One-step greedy into most valuable frontier/tempo cell
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)

        if cell in selfT:
            base = 0.0
        elif cell in unclaimed:
            base = 6.0
        elif cell in oppT:
            base = 5.0  # flipping on entry gives immediate swing
        else:
            base = 1.0  # unknown -> likely unclaimed/neutral

        # Prefer moves that keep distance advantage over opponent
        adv = man(ox, oy, nx, ny) - man(sx, sy, nx, ny)
        tempo = 0.8 * adv

        # Small penalty if surrounded by obstacles (dead-end tendency)
        adj_obs = 0
        for ddx, ddy in moves:
            ax, ay = nx + ddx, ny + ddy
            if not inb(ax, ay) or (ax, ay) in obstacles:
                adj_obs += 1
        dead = -0.05 * adj_obs

        # Bonus for nudging toward unclaimed cells (deterministic targetless heuristic)
        # Use closest unclaimed distance as proxy
        if unclaimed:
            dmin = 10**9
            for tx, ty in unclaimed:
                if (tx, ty) in obstacles:
                    continue
                d = man(nx, ny, tx, ty)
                if d < dmin:
                    dmin = d
            near = -0.12 * dmin
        else:
            near = 0.0

        val = base + tempo + dead + near
        if val > best[0]:
            best = (val, dx, dy)

    # If all moves invalid, stay put
    return [int(best[1]), int(best[2])]