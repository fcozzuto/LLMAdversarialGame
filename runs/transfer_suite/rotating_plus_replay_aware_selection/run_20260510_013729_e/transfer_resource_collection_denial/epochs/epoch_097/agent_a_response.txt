def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obst

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    def best_next_dist(px, py, tx, ty):
        bestd = 10**9
        for mdx, mdy in moves:
            nx, ny = px + mdx, py + mdy
            if not legal(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
        if bestd == 10**9:
            return man(px, py, tx, ty)
        return bestd

    def advantage_for_target(tx, ty):
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        # Predict 1 step ahead (opponent moves greedily toward same target).
        s_next = best_next_dist(sx, sy, tx, ty)
        o_next = best_next_dist(ox, oy, tx, ty)
        # Prefer being closer next turn; break ties by shorter own distance now.
        return (o_next - s_next, -(sd))

    # Choose target with maximum predicted advantage; deterministic tie-break.
    best_t = None
    best_key = None
    for rx, ry in resources:
        key = advantage_for_target(rx, ry)
        if best_key is None or key > best_key or (key == best_key and (rx, ry) < best_t):
            best_key = key
            best_t = (rx, ry)
    tx, ty = best_t

    # Choose our move that maximizes predicted advantage after our move.
    best_move = (0, 0)
    best_score = None
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not legal(nx, ny):
            continue
        s_next = man(nx, ny, tx, ty)
        # Opponent predicted next distance: greedy to same target from current pos.
        o_next = best_next_dist(ox, oy, tx, ty)
        score = (o_next - s_next, -s_next, mdx, mdy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]