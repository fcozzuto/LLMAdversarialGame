def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    resources_sorted = sorted(resources)
    best_t = None
    best_key = None

    for rx, ry in resources_sorted:
        if (rx, ry) in obstacles:
            continue
        my = dist(sx, sy, rx, ry)
        op = dist(ox, oy, rx, ry)
        secure = my <= op
        # Prefer secure resources first; then smaller my-time; then larger op-my gap (denial).
        key = (0 if secure else 1, my, -(op - my), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        new_my = dist(nx, ny, tx, ty)
        new_op = dist(ox, oy, tx, ty)
        secure = new_my <= new_op
        # Prefer keeping/creating a secure race; then reduce my time; then increase denial.
        key = (0 if secure else 1, new_my, -(new_op - new_my), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]