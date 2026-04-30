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

    # Priority: if can reach a resource, move toward closest resource not adjacent to opponent
    if resources:
        resources_sorted = sorted(resources, key=lambda r: dist(me, r))
        for rr in resources_sorted:
            # prefer step that reduces distance to rr
            best = None
            best_score = -10**9
            for dx, dy in legal:
                nx, ny = sx + dx, sy + dy
                nd = dist((nx, ny), rr)
                os_dist = dist((nx, ny), opp)
                # discourage moving towards opponent if opponent is close
                score = -nd - (0 if os_dist > 1 else 100)
                if score > best_score:
                    best_score = score
                    best = (dx, dy)
            if best is not None:
                return [best[0], best[1]]

    # Otherwise, simple approach: move toward opponent to pressure, but avoid direct collision
    best_move = None
    best_score = -10**9
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_to_opp = dist((nx, ny), opp)
        # prefer reducing distance to opponent but not moving into exact same tile
        score = -d_to_opp
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    if best_move is not None:
        return [best_move[0], best_move[1]]

    return [0, 0]