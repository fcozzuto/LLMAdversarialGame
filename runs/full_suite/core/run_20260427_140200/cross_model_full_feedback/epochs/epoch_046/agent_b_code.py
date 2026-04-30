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

    def dist_cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best = None
    best_score = -10**9

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # Score: closer to resource and farther from opponent
            d_me = dist_cheb((nx, ny), max(resources, key=lambda r: dist_cheb((nx, ny), r)))
            d_res = min(dist_cheb((nx, ny), r) for r in resources)
            d_opp = dist_cheb((nx, ny), (ox, oy))
            score = -d_res * 2 + d_me - d_opp * 0.5
            if score > best_score:
                best_score = score
                best = (dx, dy)

    if best is None:
        # If no resource-good move, head toward resources or strategic center away from opponent
        target = None
        if resources:
            target = min(resources, key=lambda r: dist_cheb((sx, sy), r))
        else:
            target = (w//2, h//2)
        best_dir = (0,0)
        best_dist = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = dist_cheb((nx, ny), target)
            if d < best_dist:
                best_dist = d
                best_dir = (dx, dy)
        best = best_dir

    dx, dy = best
    # Ensure in bounds and not illegal; if illegal, fallback to stay or safe step
    nx, ny = sx + dx, sy + dy
    if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
        dx, dy = 0, 0
    return [dx, dy]