def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

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

    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = None
    best_score = -10**9

    op = (ox, oy)

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        pos = (nx, ny)

        # distance to opponent after move
        dist_to_op = dist(pos, op)

        # nearest resource distance after move
        next_res_dist = 10**9
        for r in resources:
            d = dist(pos, r)
            if d < next_res_dist:
                next_res_dist = d
        # prefer moves that reduce distance to opponent only modestly if can grab resource soon
        # scoring: closer to resource significantly, then keep distance from opponent reasonable
        score = 0
        if next_res_dist < 10**9:
            score -= next_res_dist * 2  # reward approaching resources
        score -= dist_to_op  # avoid giving too much space to opponent
        # slight bias to staying closer to center to control resource map
        center_dist = dist(pos, (w//2, h//2))
        score -= center_dist * 0  # neutral

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]