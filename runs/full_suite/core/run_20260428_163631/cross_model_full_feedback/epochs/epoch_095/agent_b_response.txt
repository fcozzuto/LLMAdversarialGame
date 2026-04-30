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

    me = (sx, sy)
    opp = (ox, oy)

    best_move = None
    best_score = None

    # Heuristic: prioritize resources, then avoid stepping adjacent to opponent unless capturing resource
    if resources:
        resources_sorted = sorted(resources, key=lambda r: dist(me, r))
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d_to_nearest = min(dist((nx, ny), r) for r in resources)
            near_opp = dist((nx, ny), opp)
            score = -d_to_nearest * 2
            if (nx, ny) in resources:
                score += 50  # collect resource
            # discourage moving next to opponent unless it helps collect
            if near_opp <= 1:
                score -= 5
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        if best_move is not None:
            return [best_move[0], best_move[1]]

    # Fallback: move toward opponent to confront occasionally, but keep simple
    # choose the legal move that minimizes distance to opponent
    best_move = legal[0]
    best_dist = dist((sx + best_move[0], sy + best_move[1]), opp)
    for dx, dy in legal:
        d = dist((sx + dx, sy + dy), opp)
        if d < best_dist:
            best_dist = d
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]