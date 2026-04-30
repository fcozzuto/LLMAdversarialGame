def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    if not resources:
        return [0, 0]

    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    obs = set((p[0], p[1]) for p in obstacles)

    def clamp(x, y):
        if x < 0: x = 0
        if x >= w: x = w - 1
        if y < 0: y = 0
        if y >= h: y = h - 1
        return x, y

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a target by contested-advantage: prefer resources we can reach sooner than opponent
    best_t = None
    best_key = None
    for r in resources:
        dme = dist((sx, sy), (r[0], r[1]))
        dop = dist((ox, oy), (r[0], r[1]))
        key = (dme - 0.9 * dop, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best_t = r

    tx, ty = best_t[0], best_t[1]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            else:
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h:
                    moves.append((dx, dy))

    def obstacle_penalty(x, y):
        # Soft penalty if near an obstacle, to encourage corridor navigation
        pen = 0
        for ax, ay in ((x+1,y), (x-1,y), (x,y+1), (x,y-1), (x+1,y+1), (x+1,y-1), (x-1,y+1), (x-1,y-1)):
            if (ax, ay) in obs:
                pen += 2
        return pen

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obs:
            score = 10**9
        else:
            # Prefer getting closer to chosen target, while keeping distance from opponent
            score = dist((nx, ny), (tx, ty)) + 0.25 * dist((nx, ny), (ox, oy)) + 0.15 * obstacle_penalty(nx, ny)
            # If we can step onto a resource this turn, strongly prefer it
            if (nx, ny) in set((r[0], r[1]) for r in resources):
                score -= 50
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]