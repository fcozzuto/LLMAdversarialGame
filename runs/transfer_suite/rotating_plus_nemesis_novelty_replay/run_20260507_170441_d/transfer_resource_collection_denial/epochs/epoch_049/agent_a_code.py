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
        return dx if dx > dy else dy  # king-move distance

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Prefer resources where we are clearly ahead; if none, pick resource where opponent is most threatened (largest lead for us).
    best = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        adv = op_d - my_d  # positive means we get there sooner/equal
        # key: maximize advantage; then smaller my distance; then position for determinism
        key = (-adv, my_d, rx, ry)  # minimizing -> best adv (largest) first
        if best is None or key < best[0]:
            best = (key, (rx, ry), adv, my_d, op_d)
    (k, (tx, ty), adv, my_d, op_d) = best

    # Choose a valid next step that reduces distance to target most; if tied, move to increase our advantage vs opponent.
    cur_score = None
    for ddx, ddy in moves:
        nx, ny = sx + ddx, sy + ddy
        if not inb(nx, ny):
            continue
        nd = dist8(nx, ny, tx, ty)
        # After our move, estimate opponent ability to that target (we don't move opponent).
        op_to = dist8(ox, oy, tx, ty)
        next_adv = op_to - nd
        # If we're behind (adv<0), prioritize moves that reduce opponent's progress by coming closer too (still toward target).
        sc = (nd, -next_adv, abs(nx - ox) + abs(ny - oy), nx, ny)
        if cur_score is None or sc < cur_score:
            cur_score = sc
            best_move = (ddx, ddy)

    return [int(best_move[0]), int(best_move[1])]