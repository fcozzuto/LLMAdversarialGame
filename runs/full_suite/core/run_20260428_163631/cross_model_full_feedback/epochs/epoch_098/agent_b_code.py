def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = [(dx, dy) for dx, dy in deltas if inb(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    me = (sx, sy)
    opp = (ox, oy)

    if resources:
        nearest = min(resources, key=lambda r: dist((sx, sy), r))
        best = None
        best_score = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            if (nx, ny) == opp:
                continue
            d = dist((nx, ny), nearest)
            o_dist = dist((nx, ny), opp)
            score = -d + o_dist * 0  # prioritize closeness to resource, avoid opponent influence
            if best_score is None or score < best_score:
                best_score = score
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    # If no resources or not beneficial, simple deterministic heuristic:
    # Move toward center while keeping distance from opponent.
    cx, cy = w // 2, h // 2
    best = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_center = dist((nx, ny), (cx, cy))
        d_opp = dist((nx, ny), opp)
        score = d_center - d_opp  # smaller is better
        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    return [0, 0]