def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    me0 = (mx, my)
    opp0 = (ox, oy)

    # Target: closest to me while delaying opponent; deterministic tie-break by coordinates.
    best_t = None
    best_key = None
    for rx, ry in resources:
        r = (rx, ry)
        dmy = dist(me0, r)
        dop = dist(opp0, r)
        key = (dmy - dop, dmy, -dop, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = r

    tx, ty = best_t
    best_move = (0, 0)
    best_move_key = None

    # Score move by: progress to target, avoid letting opponent become strictly better, and reduce opponent targeting.
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not legal(nx, ny):
            continue
        nm = (nx, ny)
        my_d = dist(nm, best_t)
        op_d = dist(opp0, best_t)

        # Where opponent would be relative to target next step (best response approximation):
        # pick minimal possible opponent distance in one move (deterministic by tie).
        best_op_next = None
        for odx, ody in moves:
            ox2, oy2 = ox + odx, oy + ody
            if legal(ox2, oy2):
                od = dist((ox2, oy2), best_t)
                if best_op_next is None or od < best_op_next:
                    best_op_next = od
        if best_op_next is None:
            best_op_next = op_d

        # If opponent can get much closer next, we penalize; also avoid staying too far from target.
        progress = my_d
        opp_adv = (best_op_next - op_d)  # how much opponent could improve (negative is good for them)
        # Also gently steer away from opponent to reduce contention.
        cont = dist(nm, opp0)

        key = (progress, opp_adv, cont, dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]