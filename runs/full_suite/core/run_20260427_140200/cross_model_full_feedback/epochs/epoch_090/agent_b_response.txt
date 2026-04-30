def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def ok(nx, ny):
        return in_bounds(nx, ny) and (nx, ny) not in obstacles
    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Simple deterministic policy:
    # 1) If can move onto a nearest resource (or closer to it), do so.
    # 2) Else move to reduce distance to opponent modestly while staying safe.
    best_dx, best_dy = 0, 0
    if resources:
        # pick nearest resource
        target = min(resources, key=lambda p: dist((p[0], p[1]), (mx, my)))
        best = None
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if not ok(nx, ny):
                continue
            d_to_res = dist((nx, ny), (target[0], target[1]))
            d_to_opp = dist((nx, ny), (ox, oy))
            score = -d_to_res*2 - d_to_opp
            if score > best_score:
                best_score = score
                best = (dx, dy)
        if best is not None:
            best_dx, best_dy = best
            return [best_dx, best_dy]

    # If no resources, move toward center while avoiding obstacles and not stepping into opponent
    center = (w//2, h//2)
    best = None
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not ok(nx, ny):
            continue
        d_to_center = dist((nx, ny), center)
        d_to_opp = dist((nx, ny), (ox, oy))
        # try to stay a bit away from opponent if possible
        score = -d_to_center - max(0, (d_to_opp - 2))
        if score > best_score:
            best_score = score
            best = (dx, dy)
    if best is not None:
        best_dx, best_dy = best
        return [best_dx, best_dy]

    # Fallback: stay
    return [0, 0]