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

    # If a resource is available, move toward the closest one while avoiding stepping onto opponent-adjacent danger
    if resources:
        resources_sorted = sorted(resources, key=lambda r: dist(me, r))
        best = None
        best_score = None
        for r in resources_sorted:
            d_me = dist(me, r)
            d_opp = dist(opp, r)
            # Score favors getting closer to resource and keeping distance from opponent
            score = -d_me + (0 if d_opp == 0 else -d_opp/100)
            if best is None or score > best_score:
                best = r
                best_score = score
        if best is not None:
            tr, tc = best
            # choose move that decreases distance to target best
            best_move = None
            best_md = None
            for dx, dy in legal:
                nx, ny = sx + dx, sy + dy
                d = abs(nx - tr) + abs(ny - tc)
                if best_md is None or d < best_md:
                    best_md = d
                    best_move = (dx, dy)
            if best_move is not None:
                return [best_move[0], best_move[1]]

    # Fallback: move away from opponent if possible, else steer toward center
    away = None
    max_dist = -1
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = dist((nx, ny), opp)
        if d > max_dist:
            max_dist = d
            away = (dx, dy)
    if away:
        return [away[0], away[1]]

    # Last resort: stay
    return [0, 0]