def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas = [(dx, dy) for dx, dy in deltas if valid(sx + dx, sy + dy)]
    if not resources or not deltas:
        return [0, 0]

    # Anti-shadow update: if opponent is clearly closer to some resource, contest it.
    best = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        gap = op_d - my_d
        # Lower is better. Phase 0: contest (op advantage large). Phase 1: secure.
        phase = 0 if gap >= 2 else 1
        # Within phase: contest smallest op advantage still big; secure smallest my distance.
        key = (phase, abs(gap) if phase == 0 else my_d, my_d if phase == 0 else op_d)
        # Tie-break by coordinates deterministically
        key = (key[0], key[1], key[2], rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Choose next step that reduces our distance to target, but also slightly increases opponent distance to it.
    best_move = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        my_to_t = dist(nx, ny, tx, ty)
        op_to_t = dist(ox, oy, tx, ty)
        # Include our progress advantage over opponent (favors routes where we get closer than opponent).
        my_to_o = dist(nx, ny, ox, oy)
        secure_bias = dist(ox, oy, tx, ty) - dist(nx, ny, tx, ty)
        score = my_to_t * 3 + (op_to_t * 0.5) - secure_bias * 0.2 + my_to_o * 0.05
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]