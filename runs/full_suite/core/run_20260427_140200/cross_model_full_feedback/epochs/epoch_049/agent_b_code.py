def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

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

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def manhattan(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # If no explicit resources, default to staying near current position
    if not resources:
        resources = [(sx, sy)]

    dirs = [(-1,-1), (0,-1), (1,-1),
            (-1,0),  (0,0),  (1,0),
            (-1,1),  (0,1),  (1,1)]

    best = None
    best_score = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Distance to nearest resource
        if resources:
            d = min(manhattan((nx, ny), r) for r in resources)
        else:
            d = 0

        # Penalty for moving closer to opponent
        od = manhattan((nx, ny), (ox, oy))

        # Prefer to move toward center when equal
        center_dist = abs(nx - w//2) + abs(ny - h//2)

        score = -d*3 - od*2 - center_dist

        # Avoid direct collision or moving into opponent
        if nx == ox and ny == oy:
            score -= 100

        if score > best_score:
            best_score = score
            best = (nx, ny)

    if best is None:
        return [0, 0]

    return [best[0]-sx, best[1]-sy]