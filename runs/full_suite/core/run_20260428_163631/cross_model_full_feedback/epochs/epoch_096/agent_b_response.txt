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
        return 0 <= x < w and 0 <= y < h

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

    me = (sx, sy)
    opp = (ox, oy)

    best_move = None
    best_score = None

    # Prefer moving toward nearest resource, then approach or avoid opponent based on distance
    if resources:
        resources_sorted = sorted(resources, key=lambda r: dist(me, r))
        target = resources_sorted[0]
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d_to_res = dist((nx, ny), target)
            d_to_opp = dist((nx, ny), opp)
            score = -d_to_res * 2 - d_to_opp  # prioritize getting resource, then distance from opponent
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        if best_move is not None:
            return [best_move[0], best_move[1]]

    # If no resources or not better, head away from opponent along a safe path
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_to_opp = dist((nx, ny), opp)
        # prefer moves increasing distance from opponent
        score = d_to_opp
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is not None:
        return [best_move[0], best_move[1]]

    return [0, 0]