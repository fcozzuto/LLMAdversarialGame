def choose_move(observation):
    def get_xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            if "x" in v and "y" in v:
                return int(v["x"]), int(v["y"])
            if "position" in v and isinstance(v["position"], (list, tuple)) and len(v["position"]) >= 2:
                return int(v["position"][0]), int(v["position"][1])
        return 0, 0

    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = get_xy(observation.get("self_position"))
    ox, oy = get_xy(observation.get("opponent_position"))

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        x, y = get_xy(o)
        obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        x, y = get_xy(r)
        resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if resources:
        tx, ty = min(resources, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        tx, ty = ox, oy

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    best_sc = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = -(abs(nx - tx) + abs(ny - ty))
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]