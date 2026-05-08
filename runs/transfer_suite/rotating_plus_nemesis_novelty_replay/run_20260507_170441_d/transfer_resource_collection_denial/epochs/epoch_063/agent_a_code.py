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
        return dx if dx > dy else dy  # king distance

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = []
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        adv = op_d - my_d
        # Primary: maximize our advantage. Secondary: prefer smaller our distance. Deterministic tie.
        key = (-(adv), my_d, rx, ry)
        best.append((key, rx, ry, adv, my_d, op_d))
    best.sort(key=lambda z: z[0])
    # Mild diversification: if top choice is risky (we are behind badly), consider 2nd.
    cand = [best[0], best[1] if len(best) > 1 else best[0]]
    target = cand[0] if cand[0][3] >= cand[1][3] - 1 else cand[1]
    _, tx, ty, _, _, _ = target

    # Pick move that improves our prospects next turn: minimize distance to target,
    # and among ties, maximize advantage versus opponent for that same target.
    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_d2 = dist8(nx, ny, tx, ty)
        op_d2 = dist8(ox, oy, tx, ty)
        adv2 = op_d2 - my_d2
        key = (my_d2, -(adv2), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]