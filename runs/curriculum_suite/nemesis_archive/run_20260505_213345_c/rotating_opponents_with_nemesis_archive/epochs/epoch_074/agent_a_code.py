def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def d8(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    my_resources = resources
    best_t = None
    best_score = None
    for r in my_resources:
        md = d8((sx, sy), r)
        od = d8((ox, oy), r)
        # Prefer resources where we're closer; otherwise, go for one that the opponent can't easily beat.
        score = (od - md) * 1000 - md
        if best_score is None or score > best_score or (score == best_score and r < best_t):
            best_score = score
            best_t = r

    tx, ty = best_t
    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)

    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = [0, 0]
    best_h = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        # Primary: reduce distance to target; Secondary: keep from being too close/next to opponent.
        h = d8((nx, ny), (tx, ty)) * 10 - d8((nx, ny), (ox, oy))
        if best_h is None or h < best_h:
            best_h = h
            best_move = [dx, dy]

    # If desired step was blocked, we already chose best feasible alternative.
    # If desired is feasible and among best, it will be selected by the heuristic anyway.
    return [int(best_move[0]), int(best_move[1])]