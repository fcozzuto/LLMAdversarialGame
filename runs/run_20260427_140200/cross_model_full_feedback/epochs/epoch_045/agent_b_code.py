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

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best_move = (0, 0)
    best_score = -10**9

    # Prefer moving toward nearest resource while keeping some distance from opponent
    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # distance to closest resource
            d_res = min(dist(nx, ny, rx, ry) for rx, ry in resources)
            # distance from opponent to that same resource (approx)
            d_opp = min(dist(ox, oy, rx, ry) for rx, ry in resources) if resources else 0
            # score: closer to resource, and keep away from opponent relative to resource
            score = -d_res
            # if moving closer to opp increases risk; reduce score if closer to opp
            score -= max(0, 1 if (abs(nx - ox) + abs(ny - oy) <= 1) else 0)
            score += 0  # placeholder for determinism
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        # no resources: move to maximize distance from opponent slightly
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            score = -(abs(nx - ox) + abs(ny - oy))
            if score > best_score:
                best_score = score
                best_move = (dx, dy)

    # Ensure within allowed deltas
    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        dx, dy = 0, 0

    return [dx, dy]