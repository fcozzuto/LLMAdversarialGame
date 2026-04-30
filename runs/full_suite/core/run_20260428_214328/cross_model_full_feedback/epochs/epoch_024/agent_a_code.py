def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    ox, oy = int(ox), int(oy)
    sx, sy = int(sx), int(sy)

    obst = set((int(p[0]), int(p[1])) for p in obstacles)
    res = [(int(p[0]), int(p[1])) for p in resources]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(nx, ny):
        return inside(nx, ny) and (nx, ny) not in obst and (nx, ny) != (ox, oy)

    def cheb(a, b):
        ax, ay = a; bx, by = b
        da = abs(ax - bx)
        db = abs(ay - by)
        return da if da >= db else db

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_val = -10**18

    # Deterministic tie-break order: earlier in moves list wins.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        val = 0

        # If we can capture (not used in ok since it forbids opponent tile), strongly prefer it.
        if (nx, ny) == (ox, oy):
            val += 10**9

        if res:
            # Prefer reducing distance to the nearest resource.
            d_now = min(cheb((sx, sy), r) for r in res)
            d_new = min(cheb((nx, ny), r) for r in res)
            val += (d_now - d_new) * 100

            # Soft attraction to a nearby resource; discourage wandering.
            target = min(res, key=lambda r: (cheb((nx, ny), r), r[0], r[1]))
            val -= cheb((nx, ny), target) * 5

        # Strategic pressure: keep closer (in Chebyshev) to opponent than they to us (when possible).
        val += (cheb((ox, oy), (nx, ny)) - cheb((ox, oy), (sx, sy))) * 3

        # Border/obstacle avoidance: slight penalty for being near obstacles.
        if obst:
            near_obst = 0
            for ax, ay in obst:
                if max(abs(ax - nx), abs(ay - ny)) <= 1:
                    near_obst += 1
            val -= near_obst * 2

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return [int(best[0]), int(best[1])]