def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    resources_sorted = sorted(resources, key=lambda r: dist((sx, sy), r))

    # If there is a resource, prefer moving toward closest while avoiding opponent's immediate threat
    if resources_sorted:
        target = resources_sorted[0]
        best = None
        best_score = -10**9
        opp = (ox, oy)
        me = (sx, sy)
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            # score based on distance to target and distance from opponent
            d_to_target = dist((nx, ny), target)
            d_to_opp = dist((nx, ny), opp)
            score = -d_to_target * 2 + d_to_opp
            if score > best_score:
                best_score = score
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    # No viable resource path or equal; move to reduce opponent distance while staying safe
    best = None
    best_score = -10**9
    opp = (ox, oy)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_opp = dist((nx, ny), opp)
        # keep distance from opponent but also bias toward center
        center_dx = abs(nx - (w-1)//2) + abs(ny - (h-1)//2)
        score = -d_opp * 2 - center_dx
        if score > best_score:
            best_score = score
            best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    return [0, 0]