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

    # Simple deterministic heuristic:
    # 1) If a resource is nearby, move toward the nearest resource.
    # 2) If opposing agent close, try to avoid collision by moving away if possible.
    # 3) Else move toward center to maximize options.
    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best = None
    best_score = -10**9

    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    # If resources present, prioritize getting closer to one resource
    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            nearest = min(resources, key=lambda r: dist((nx, ny), r))
            d_to_res = dist((nx, ny), nearest)
            d_from_opp = dist((nx, ny), (ox, oy))
            score = -d_to_res * 2 + d_from_opp  # closer to resource, farther from opponent
            if score > best_score:
                best_score = score
                best = (dx, dy)

    if best is None:
        # No legal move toward resource; try to avoid opponent
        safe_moves = []
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d_from_opp = dist((nx, ny), (ox, oy))
            safe_moves.append(((dx, dy), d_from_opp))
        if safe_moves:
            # pick move maximizing distance from opponent
            best = max(safe_moves, key=lambda t: t[1])[0]
        else:
            best = (0, 0)

    dx, dy = best
    return [dx, dy]