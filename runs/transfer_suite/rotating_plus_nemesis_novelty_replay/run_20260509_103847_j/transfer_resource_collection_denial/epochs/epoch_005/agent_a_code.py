def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    def manhattan(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Target resources we can contest: arrive earlier than opponent, prefer safer advantage.
    best = None
    for rx, ry in resources:
        sd = manhattan(sx, sy, rx, ry)
        od = manhattan(ox, oy, rx, ry)
        # Primary: maximize opponent-arrival advantage (od - sd)
        # Secondary: minimize our arrival time sd
        # Tertiary: deterministic tie by coordinates
        key = (-(od - sd), sd, rx, ry)  # negative to make "smaller key" best when od-sd largest
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Greedy step toward target while maximizing post-move advantage to the target.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd_new = manhattan(nx, ny, tx, ty)
        od = manhattan(ox, oy, tx, ty)
        # Prefer larger (od - sd_new); then smaller sd_new; then deterministic dx,dy ordering
        key = (-(od - sd_new), sd_new, abs(dx) + abs(dy), dx, dy, nx, ny)
        if best_m is None or key < best_m[0]:
            best_m = (key, (dx, dy))

    if best_m is None:
        return [0, 0]
    dx, dy = best_m[1]
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [dx, dy]