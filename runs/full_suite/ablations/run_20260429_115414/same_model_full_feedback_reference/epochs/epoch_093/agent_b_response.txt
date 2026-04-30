def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not legal(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Select a target that we are closer to than the opponent (if possible), else pick the least-bad alternative.
    targets = resources if resources else [(W // 2, H // 2)]
    best_t = targets[0]
    best_adv = -10**9
    best_abs = 10**9
    for tx, ty in targets:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        adv = ds - do  # negative is good (we are closer)
        absd = ds
        if (adv < best_adv) or (adv == best_adv and absd < best_abs):
            best_adv = adv
            best_abs = absd
            best_t = (tx, ty)

    tx, ty = best_t

    # Evaluate moves: maximize progress to target, but avoid giving opponent a too-easy access.
    # Deterministic tie-breaking uses fixed move order.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds_new = cheb(nx, ny, tx, ty)
        do_now = cheb(ox, oy, tx, ty)
        adv_new = ds_new - do_now
        dist_opp = cheb(nx, ny, ox, oy)

        # Primary: make adv_new as negative as possible; secondary: reduce ds_new; tertiary: increase distance from opponent.
        score = (-adv_new) * 100 - ds_new * 2 + dist_opp

        # Small penalty for moving into immediate vicinity of opponent unless it improves target more.
        opp_close = 1 if dist_opp <= 1 else 0
        score -= opp_close * 5

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]