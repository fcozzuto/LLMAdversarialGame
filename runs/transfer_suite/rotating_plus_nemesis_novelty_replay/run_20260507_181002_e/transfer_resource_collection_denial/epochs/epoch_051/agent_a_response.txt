def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def to_xy(v, default=None):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return (int(p[0]), int(p[1]))
        return default

    sx, sy = to_xy(observation.get("self_position", None), (0, 0))
    ox, oy = to_xy(observation.get("opponent_position", None), (sx, sy))

    obs = set()
    for o in observation.get("obstacles", []) or []:
        xy = to_xy(o, None)
        if xy is None:
            continue
        x, y = xy
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = []
    for r in observation.get("resources", []) or []:
        xy = to_xy(r, None)
        if xy is None:
            continue
        x, y = xy
        if free(x, y):
            resources.append((x, y))

    if not resources:
        dx, dy = 0, 0
        for dxx in (-1, 0, 1):
            for dyy in (-1, 0, 1):
                if dxx == 0 and dyy == 0:
                    continue
                nx, ny = sx + dxx, sy + dyy
                if free(nx, ny):
                    dx, dy = dxx, dyy
                    break
            if dx or dy:
                break
        return [dx, dy]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_cell = None
    best_key = None
    for tx, ty in resources:
        d_self = md((sx, sy), (tx, ty))
        d_opp = md((ox, oy), (tx, ty))
        key = (d_opp - d_self, -d_self)
        if best_key is None or key > best_key:
            best_key = key
            best_cell = (tx, ty)

    tx, ty = best_cell

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dxx, dyy in deltas:
        nx, ny = sx + dxx, sy + dyy
        if not free(nx, ny):
            continue
        self_d = md((nx, ny), (tx, ty))
        opp_d = md((ox, oy), (tx, ty))
        arrive = 1 if (nx == tx and ny == ty) else 0

        # Prefer moves that reduce own distance; break ties by reducing opponent's relative advantage.
        # Also add slight obstacle-avoidance: prefer moves with more free neighboring cells.
        free_neighbors = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if free(nx + ax, ny + ay):
                    free_neighbors += 1

        score = (arrive, (opp_d - self_d), -self_d, free_neighbors)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dxx, dyy)

    return [int(best_move[0]), int(best_move[1])]