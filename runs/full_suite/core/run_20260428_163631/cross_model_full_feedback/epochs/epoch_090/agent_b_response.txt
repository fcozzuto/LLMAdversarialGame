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

    # If there is at least one resource, move toward closest resource while staying safe from opponent
    if resources_sorted:
        target = resources_sorted[0]
        best = None
        best_score = -10**9
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d_to_target = dist((nx, ny), target)
            # Prefer moves that reduce distance to target
            score = -d_to_target
            # Slight penalty if moving closer to opponent
            d_to_op = dist((nx, ny), (ox, oy))
            score -= d_to_op * 0.1
            if best is None or score > best_score:
                best = (dx, dy)
                best_score = score
        return [best[0], best[1]]

    # No resources visible: simple aggressive approach: move towards center while keeping distance from opponent
    cx, cy = (w-1)//2, (h-1)//2
    best = None
    best_score = -10**9
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_to_center = dist((nx, ny), (cx, cy))
        d_to_op = dist((nx, ny), (ox, oy))
        score = -d_to_center - d_to_op * 0.5
        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score
    return [best[0], best[1]]