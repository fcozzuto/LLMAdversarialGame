def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources_in = observation.get("resources", []) or []
    obstacles_in = observation.get("obstacles", []) or []

    resources = []
    for p in resources_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    obstacles = set()
    for p in obstacles_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Pick best target by who is closer (tie-break: closer to opponent advantage, then self distance)
    best_target = None
    best_key = None
    for rx, ry in resources:
        k = (dist(ox, oy, rx, ry) - dist(sx, sy, rx, ry), -dist(sx, sy, rx, ry), rx, ry)
        if best_key is None or k > best_key:
            best_key = k
            best_target = (rx, ry)

    tx, ty = best_target

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    # Choose move that improves self progress to target; if blocked, stays effectively (engine keeps in place)
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        self_d = dist(nx, ny, tx, ty)
        opp_d = dist(ox, oy, tx, ty)
        # Prefer winning advantage; then reduce distance; then deterministic preference by move order
        score = ((opp_d - self_d), -self_d, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]