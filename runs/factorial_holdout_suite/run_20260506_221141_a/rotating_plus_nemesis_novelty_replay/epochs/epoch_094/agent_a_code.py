def choose_move(observation):
    def xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return 0, 0

    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)
    sx, sy = xy(observation.get("self_position"))
    ox, oy = xy(observation.get("opponent_position"))

    obstacles = set()
    for it in observation.get("obstacles") or []:
        x, y = xy(it)
        if 0 <= x < gw and 0 <= y < gh:
            obstacles.add((x, y))

    resources = []
    for it in observation.get("resources") or []:
        x, y = xy(it)
        if 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        if (nx, ny) in obstacles:
            continue
        d_res = min(manhattan((nx, ny), r) for r in resources)
        d_opp = manhattan((nx, ny), (ox, oy))
        val = d_res * 1000 - d_opp  # primary: closer to resource; secondary: farther from opponent
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]