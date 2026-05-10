def choose_move(observation):
    W = int(observation.get("grid_width", 0) or 0)
    H = int(observation.get("grid_height", 0) or 0)
    if W <= 0 or H <= 0:
        return [0, 0]

    def xy(v, d0=0, d1=0):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict) and "x" in v and "y" in v:
            return int(v["x"]), int(v["y"])
        return d0, d1

    sx, sy = xy(observation.get("self_position", (0, 0)))
    ox, oy = xy(observation.get("opponent_position", (0, 0)))

    obstacles = set()
    for c in (observation.get("obstacles") or []):
        x, y = xy(c, None, None)
        if x is not None and y is not None and 0 <= x < W and 0 <= y < H:
            obstacles.add((x, y))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        x, y = xy(p, None, None)
        if x is not None and 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
            unclaimed.add((x, y))

    resources = set()
    for p in (observation.get("resources") or []):
        x, y = xy(p, None, None)
        if x is not None and 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
            resources.add((x, y))

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sc = 0
        if (nx, ny) in unclaimed:
            sc += 12
        if (nx, ny) in resources:
            sc += 6
        sc -= md(nx, ny, ox, oy)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    if best is not None:
        return best

    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            return [dx, dy]
    return [0, 0]