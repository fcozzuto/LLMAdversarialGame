def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx + dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_score = None

    # Prefer moving toward nearest resource if safe; else approach center
    if resources:
        nearest = min(resources, key=lambda r: dist((mx, my), r))
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if not in_bounds(nx, ny):
                continue
            d = dist((nx, ny), nearest)
            score = -d
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)

    if best is None:
        # no safe move toward resource, head toward center while avoiding obstacles
        center = (w // 2, h // 2)
        dx = center[0] - mx
        dy = center[1] - my
        step_x = 1 if dx > 0 else -1 if dx < 0 else 0
        step_y = 1 if dy > 0 else -1 if dy < 0 else 0
        cand = [(step_x, step_y), (step_x, 0), (0, step_y), (step_x, -step_y), (-step_x, step_y)]
        for dxn, dyn in cand:
            nx, ny = mx + dxn, my + dyn
            if in_bounds(nx, ny):
                best = (dxn, dyn)
                break

    if best is None:
        best = (0, 0)

    return [best[0], best[1]]