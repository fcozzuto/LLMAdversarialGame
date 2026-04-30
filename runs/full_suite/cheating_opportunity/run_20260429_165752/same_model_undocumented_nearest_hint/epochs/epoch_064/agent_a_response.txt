def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = ox, oy
    else:
        # New policy: choose resource with best lead over opponent (maximize d_op - d_me),
        # tie-break by closer to us (min d_me), then lexicographic.
        best = None
        best_key = None
        for tx, ty in resources:
            d_me = cheb(sx, sy, tx, ty)
            d_op = cheb(ox, oy, tx, ty)
            key = (d_op - d_me, -d_me, -tx, -ty)
            if best_key is None or key > best_key:
                best_key = key
                best = (tx, ty)
        tx, ty = best

    # Greedy step toward target while also respecting "threat": reduce opponent's potential lead after move.
    cur_d_me = cheb(sx, sy, tx, ty)
    cur_d_op = cheb(ox, oy, tx, ty)

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_me = cheb(nx, ny, tx, ty)

        # Threat response: prefer moves that reduce our time-to-resource and, secondarily,
        # increase opponent's relative difficulty (d_op_after - d_me).
        # We assume opponent continues greedily toward same target; approximate with current opponent distance.
        threat_val = (cur_d_op - d_me)  # monotone with our improvement
        # Also softly avoid stepping into cells that are closer to the opponent than we are.
        self_close = 0
        if d_me > 0:
            d_opp_to_here = cheb(ox, oy, nx, ny)
            if d_opp_to_here < d_me:
                self_close = 1

        # Primary: minimize d_me; Secondary: maximize threat_val; Tertiary: deterministic tie-break.
        val = (-d_me, threat_val, -self_close, -dx, -dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]