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

    if resources:
        # Move toward closest resource, avoiding stepping onto opponent-adjacent danger
        resources_sorted = sorted(resources, key=lambda r: dist(me, r))
        for r in resources_sorted:
            rx, ry = r
            # prefer legal moves that reduce distance to resource
            candidates = []
            for dx, dy in legal:
                nx, ny = sx + dx, sy + dy
                nd = dist((nx, ny), r)
                candidates.append(((dx, dy), nd))
            if not candidates:
                continue
            candidates.sort(key=lambda t: t[1])
            # pick closest to resource
            dx, dy = candidates[0][0]
            # ensure not moving onto opponent's current cell
            if (sx + dx, sy + dy) == opp:
                continue
            best_move = [dx, dy]
            break
        if best_move is not None:
            return best_move

        # Fallback: move to maximize distance from opponent
    # No resources or couldn't approach, move away from opponent if possible
    best = None
    best_dist = -1
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = dist((nx, ny), opp)
        if d > best_dist:
            best_dist = d
            best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    return [0, 0]