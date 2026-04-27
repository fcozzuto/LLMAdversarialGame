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

    def score_pos(nx, ny):
        if resources:
            best = None
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if best is None or d < best:
                    best = d
            return -best
        return 0

    # Prefer approaching closest resource while not colliding with opponent or obstacles.
    best_move = [0, 0]
    best_value = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # discourage moving towards opponent if it can lead to collision
        # simple rule: avoid stepping into opponent's cell
        if (nx, ny) == (ox, oy):
            continue
        val = score_pos(nx, ny)
        # also penalize staying if moving towards resource is possible
        if resources:
            dist_to_opp = man(nx, ny, ox, oy)
            # small penalty if too close to opponent
            if dist_to_opp <= 1:
                val -= 1
        if val > best_value:
            best_value = val
            best_move = [dx, dy]

    return best_move