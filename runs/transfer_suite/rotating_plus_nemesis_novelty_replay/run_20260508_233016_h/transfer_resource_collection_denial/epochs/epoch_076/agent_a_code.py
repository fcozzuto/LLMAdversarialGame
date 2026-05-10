def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_key = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        if my_d < op_d:
            key = (0, my_d, op_d, rx, ry)  # secure
        else:
            key = (1, -(op_d - my_d), my_d, op_d, rx, ry)  # deny
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best
    secure = best_key[0] == 0

    my_target_d = dist(sx, sy, tx, ty)
    best_move = None
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd_my = dist(nx, ny, tx, ty)
        nd_op = dist(nx, ny, ox, oy)

        # Primary: get closer to target (secure) or avoid giving opponent an easy path (deny).
        # Tie-breakers: avoid moving away too much; prefer positions that also reduce our distance-to-opponent risk slightly.
        if secure:
            key = (0, nd_my, -nd_op, nx, ny)
        else:
            # Deny: still move toward target, but prioritize making our move less favorable to the opponent.
            # Since we don't model opponent moves precisely, use (op-target gap) proxy via our proximity change to opponent.
            gap_proxy = dist(ox, oy, tx, ty) - nd_my
            key = (1, -gap_proxy, nd_my, -nd_op, nx, ny)

        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]