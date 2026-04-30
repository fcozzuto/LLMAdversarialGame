def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    # Simple deterministic policy:
    # 1) If a resource is available, move towards the closest resource while avoiding opponent capture.
    if resources:
        nearest = min(resources, key=lambda r: dist((sx, sy), r))
        best = None
        best_score = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            if (nx, ny) == opp:
                continue
            d = dist((nx, ny), nearest)
            opp_dist = dist((nx, ny), opp)
            # score favors closer to resource and further from opponent
            score = -d + opp_dist
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    # 2) If no resource or no safe move toward it, pursue center-ish approach while avoiding obstacle and opponent.
    target_x = w // 2
    target_y = h // 2
    best = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) == opp:
            continue
        d = dist((nx, ny), (target_x, target_y))
        adist = dist((nx, ny), opp)
        score = -d - adist
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    # 3) Fallback: move away from opponent if possible, else stay.
    best = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) == opp:
            continue
        d = dist((nx, ny), opp)
        score = d
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    return [0, 0]