def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            if "position" in v and v["position"] is not None:
                p = v["position"]
                return int(p[0]), int(p[1])
            if "x" in v and "y" in v:
                return int(v["x"]), int(v["y"])
        return (0, 0)

    sx, sy = xy(observation.get("self_position") or [0, 0])
    ox, oy = xy(observation.get("opponent_position") or [0, 0])

    obstacles = set()
    for it in observation.get("obstacles", []) or []:
        p = xy(it.get("position") if isinstance(it, dict) and "position" in it else it)
        if 0 <= p[0] < w and 0 <= p[1] < h:
            obstacles.add(p)

    resources = []
    for it in observation.get("resources", []) or []:
        p = xy(it.get("position") if isinstance(it, dict) and "position" in it else it)
        if 0 <= p[0] < w and 0 <= p[1] < h and p not in obstacles:
            resources.append(p)

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        if resources:
            dres = min(manh((nx, ny), r) for r in resources)
            dop = man((nx, ny), (ox, oy))
            key = (dres, -dop, dx, dy)
        else:
            key = (-man((nx, ny), (ox, oy)), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]