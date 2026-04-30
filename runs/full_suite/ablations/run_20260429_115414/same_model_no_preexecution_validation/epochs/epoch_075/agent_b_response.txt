def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        tx, ty = (w // 2, h // 2) if (sx + sy) > (ox + oy) else (w // 2 - 1, h // 2 - 1)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Select target that maximizes "advantage": opponent farther than us, with tie-breaker by self closeness.
    best = None
    best_adv = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        adv = do - ds  # higher means we can arrive earlier or contest advantage
        if best is None or adv > best_adv or (adv == best_adv and (ds < cheb(sx, sy, best[0], best[1]))):
            best = (tx, ty)
            best_adv = adv

    tx, ty = best
    # Evaluate actual move choices: primary minimize distance to target; secondary keep improving advantage; tertiary keep out of obstacles.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        ns = cheb(nx, ny, tx, ty)
        # moving should not give opponent a better immediate advantage than us
        no = cheb(ox, oy, tx, ty)
        my_adv_after = no - ns
        score = (-ns, -my_adv_after, abs((tx - nx)) + abs((ty - ny)), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If all moves filtered out (rare), fall back to stay.
    if best_score is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]