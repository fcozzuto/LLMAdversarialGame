def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles if p is not None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Choose target that we can reach relatively earlier than opponent; tie-break by shortest our distance.
    best_key = None
    best_t = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        adv = op_d - my_d  # positive means we are closer/equal than opponent
        # Prefer: largest advantage, then smaller our distance, then deterministic position
        key = (-adv, my_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    # If we are not meaningfully ahead, attempt interception by moving toward a "leading point"
    # near where opponent would be when we get there: target point is the resource itself,
    # but step choice prefers moves that reduce our distance most while also not letting opponent gain more.
    def opp_gain(nextx, nexty):
        # how much closer opponent would be to the chosen target versus us (negative is good for us)
        return dist8(ox, oy, tx, ty) - dist8(nextx, nexty, tx, ty)

    cur_d = dist8(sx, sy, tx, ty)
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist8(nx, ny, tx, ty)
        # Score: primary reduce our distance; secondary ensure we don't worsen relative race too much; deterministic tie-break.
        primary = d - cur_d  # negative is good
        score = (primary, opp_gain(nx, ny), abs(nx - tx) + abs(ny - ty), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]