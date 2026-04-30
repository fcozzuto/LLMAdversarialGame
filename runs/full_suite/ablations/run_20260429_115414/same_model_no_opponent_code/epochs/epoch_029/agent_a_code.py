def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    def to_xy(v):
        try:
            x, y = v
            x = int(x); y = int(y)
            return x, y
        except Exception:
            return 0, 0

    sx, sy = to_xy(observation.get("self_position", (0, 0)))
    ox, oy = to_xy(observation.get("opponent_position", (0, 0)))

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dy = ay - by
        return dx * dx + dy * dy

    self_pos = (sx, sy)
    opp_pos = (ox, oy)

    if resources:
        nearest = min(resources, key=lambda r: dist2(self_pos, r))
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            np = (nx, ny)
            # prioritize immediate improvement toward a resource; tie-break by pushing away from opponent
            key = (dist2(np, nearest), dist2(np, opp_pos))
            if best is None or key < best[0]:
                best = (key, dx, dy)
            if dist2(np, nearest) == 0:
                return [dx, dy]
        if best is not None:
            return [best[1], best[2]]

    # No accessible resources: move toward opponent if possible; otherwise stay.
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        np = (nx, ny)
        key = (dist2(np, opp_pos), dist2(np, self_pos))
        if best is None or key < best[0]:
            best = (key, dx, dy)
    if best is not None:
        return [best[1], best[2]]
    return [0, 0]