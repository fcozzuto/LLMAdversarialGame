def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    res_set = set(tuple(r) for r in resources)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    # Immediate pickup
    for dx, dy, nx, ny in valid:
        if (nx, ny) in res_set:
            return [dx, dy]

    # Choose best target resource: reach earlier than opponent, prefer closer and "intercept" on opponent row.
    best_target = None
    best_score = None
    opp_on_row = (oy == sy)  # just a slight contextual bias
    for rx, ry in resources:
        dme = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # prefer positions we can take sooner; weight intercept if resource is on opponent's current row
        score = (do - dme) * 10 + (do == dme) * 2 - dme
        if ry == oy:
            score += 3
        if opp_on_row:
            score += 1
        if best_score is None or score > best_score:
            best_score = score
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    # Pick the move that most improves my progress to target, and if possible reduces opponent's advantage.
    best_move = (0, 0, sx, sy)
    best_val = None
    for dx, dy, nx, ny in valid:
        myd = cheb(nx, ny, tx, ty)
        old_my = cheb(sx, sy, tx, ty)
        # estimate opponent impact as if opponent stays (deterministic, local)
        do = cheb(ox, oy, tx, ty)
        # want smaller my distance; also want to not let opponent be much sooner
        val = -(myd) * 5 + (do - myd) * 2 + (myd < old_my) * 1
        # extra preference to land on opponent row if it aligns with target
        if ty == oy and ny == oy:
            val += 2
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy, nx, ny)

    return [best_move[0], best_move[1]]