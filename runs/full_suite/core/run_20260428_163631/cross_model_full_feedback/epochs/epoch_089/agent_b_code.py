def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obstacles.add((x, y))

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

    def dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    resources_sorted = sorted(resources, key=lambda r: dist((sx, sy), r))

    # If there is a resource, try to move toward the closest resource while avoiding letting opponent reach sooner.
    if resources_sorted:
        target = resources_sorted[0]
        # choose legal move that minimizes distance to target; tie-breaker: prefer moves that increase distance to opponent if possible
        best = None
        best_score = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d_to_target = dist((nx, ny), target)
            d_to_opp = dist((nx, ny), (ox, oy))
            # score: prioritize smaller distance to target; if equal, larger distance to opponent
            score = (d_to_target, -d_to_opp)
            if best is None or score < best_score:
                best = (dx, dy)
                best_score = score
        if best is not None:
            return [best[0], best[1]]

    # Fallback: move to maximize distance from opponent, within legal moves
    best = legal[0]
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_to_opp = dist((nx, ny), (ox, oy))
        if best_score is None or d_to_opp > best_score:
            best = (dx, dy)
            best_score = d_to_opp
    return [best[0], best[1]]