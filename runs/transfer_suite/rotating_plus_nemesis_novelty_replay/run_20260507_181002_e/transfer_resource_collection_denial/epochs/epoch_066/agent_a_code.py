def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def get_xy(v, default=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", v.get("xy", None)))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return (int(p[0]), int(p[1]))
            if "x" in v and "y" in v:
                return (int(v["x"]), int(v["y"]))
        return default

    sx, sy = get_xy(observation.get("self_position", None), (0, 0))
    ox, oy = get_xy(observation.get("opponent_position", None), (sx, sy))

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        x, y = get_xy(o, (None, None))
        if x is not None and y is not None and 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        x, y = get_xy(r, (None, None))
        if x is not None and y is not None and free(x, y):
            resources.append((x, y))

    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        if resources:
            tx, ty = min(resources, key=lambda p: abs(p[0] - nx) + abs(p[1] - ny))
            val = -(abs(tx - nx) + abs(ty - ny)) + (1 if (nx, ny) == (tx, ty) else 0)
        else:
            val = -abs(ox - nx) - abs(oy - ny)
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]