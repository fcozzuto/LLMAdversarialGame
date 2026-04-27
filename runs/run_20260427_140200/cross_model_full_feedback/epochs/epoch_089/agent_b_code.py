def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
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

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Try to collect nearest resource while avoiding obstacles and staying away from opponent
    if resources:
        tx, ty = min(resources, key=lambda p: dist((p[0], p[1]), (mx, my)))
        best = None
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if not in_bounds(nx, ny): 
                continue
            if (nx, ny) in obstacles:
                continue
            # score: prefer getting closer to resource, then keep distance from opponent
            d_to_res = dist((nx, ny), (tx, ty))
            d_to_opp = dist((nx, ny), (ox, oy))
            score = -d_to_res*2 - d_to_opp
            if best is None or score > best_score:
                best = (dx, dy)
                best_score = score
        if best is not None:
            return [best[0], best[1]]

    # If no resources or could not approach safely, seek to improve positional advantage
    # Move toward center while avoiding obstacles and not stepping onto opponent
    cx, cy = w // 2, h // 2
    best = None
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        if nx == ox and ny == oy:
            continue
        d_to_center = dist((nx, ny), (cx, cy))
        d_to_opp = dist((nx, ny), (ox, oy))
        score = -d_to_center*3 - d_to_opp*2
        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score
    if best is not None:
        return [best[0], best[1]]

    # Fallback: stay or move away from opponent if possible
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles and not (nx == ox and ny == oy):
            return [dx, dy]

    return [0, 0]