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

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1,  0), (0,  0), (1,  0),
            (-1,  1), (0,  1), (1,  1)]

    def man(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx + dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist_to_resource(nx, ny):
        if not resources:
            return float('inf')
        best = None
        for rx, ry in resources:
            d = man(nx, ny, rx, ry)
            if best is None or d < best:
                best = d
        return best

    best_dx = 0
    best_dy = 0
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_res = dist_to_resource(nx, ny)
        # If moving closer to opponent is bad, discourage approaching
        # Prefer positions that are not too close to opponent and closer to resources
        odist = man(nx, ny, ox, oy)
        score = (d_res * 3) - odist  # heuristic weight
        if best_score is None or score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]