def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    role = observation.get("self_role", "pursuer")

    deltas = [(-1, -1), (1, 1), (-1, 1), (1, -1), (-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if role == "evader":
        tx, ty = max(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))
        aimx, aimy = tx, ty
        best = None
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = dist2(nx, ny, ox, oy)  # maximize distance
            v += 0.05 * dist2(nx, ny, aimx, aimy)  # keep pushing toward corner
            v -= 0.02 * (abs(nx - aimx) + abs(ny - aimy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # pursuer
    vx = 1 if ox > sx else (-1 if ox < sx else 0)
    vy = 1 if oy > sy else (-1 if oy < sy else 0)
    aimx = ox + vx  # predict evader running away from us
    aimy = oy + vy
    aimx = 0 if aimx < 0 else (w - 1 if aimx >= w else aimx)
    aimy = 0 if aimy < 0 else (h - 1 if aimy >= h else aimy)

    # also bias toward cutting off near walls/obstacles: choose move that reduces distance to aim and blocks corners
    best = None
    bestv = 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = dist2(nx, ny, aimx, aimy)  # primary intercept
        v += 0.15 * dist2(nx, ny, ox, oy)  # secondary: stay close
        # obstacle/wall pressure: prefer positions with fewer escape options for evader (lower local mobility)
        mob = 0
        for ddx, ddy in deltas:
            tx2, ty2 = nx + ddx, ny + ddy
            if inb(tx2, ty2):
                mob += 1
        v += 0.03 * mob
        if v < bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]