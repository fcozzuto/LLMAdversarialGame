def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if (0, 0) not in moves:
        moves.append((0, 0))

    if not resources:
        return [0, 0]

    # Heuristic: prioritize getting closer to a resource while staying farther from opponent.
    # Also softly avoid stepping next to obstacles.
    adj8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def obstacle_pen(x, y):
        pen = 0
        for dx, dy in adj8:
            if (x + dx, y + dy) in obstacles:
                pen += 1
        return pen

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # choose nearest resource from the next position
        mind = 10**9
        for rx, ry in resources:
            d = dist(nx, ny, rx, ry)
            if d < mind:
                mind = d

        # discourage moving toward opponent; strong if very close
        do = dist(nx, ny, ox, oy)
        enemy_term = 0
        if do <= 2:
            enemy_term = 20 - 5 * do
        elif do <= 4:
            enemy_term = 6 - 1.5 * do

        score = mind * 3 + obstacle_pen(nx, ny) * 2 + enemy_term
        # tie-break: prefer moves that increase distance to opponent
        tie = -(do)
        key = (score, tie, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]