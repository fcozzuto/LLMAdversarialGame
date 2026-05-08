def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is not None:
            obst.add((p[0], p[1]))
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    if not resources:
        return [0, 0]

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my = (nx, ny)
        # Prefer moves that get to some resource earlier than opponent.
        local_best = None
        for rx, ry in resources:
            r = (rx, ry)
            d_my = dist(my, r)
            d_op = dist((ox, oy), r)
            # Larger advantage better; then closer to resource; then farther from opponent.
            score = (d_op - d_my, -d_my, dist((ox, oy), my))
            if local_best is None or score > local_best:
                local_best = score
        # Small penalty for staying still to reduce dithering.
        total = (local_best[0], local_best[1], local_best[2]) if local_best is not None else (-10, 0, 0)
        if dx == 0 and dy == 0:
            total = (total[0] - 0.01, total[1], total[2])
        if best_score is None or total > best_score:
            best_score = total
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]