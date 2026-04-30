def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
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
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Select target resource where we have the biggest distance advantage (deterministic tie-break).
    best_res = resources[0]
    best_adv = -10**9
    for (x, y) in resources:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        adv = od - sd
        if adv > best_adv or (adv == best_adv and (x < best_res[0] or (x == best_res[0] and y < best_res[1]))):
            best_adv, best_res = adv, (x, y)

    tx, ty = best_res
    cur_sd = cheb(sx, sy, tx, ty)
    cur_od = cheb(ox, oy, tx, ty)

    best_move = (0, 0)
    best_score = -10**18
    # Move evaluation: go toward target, discourage moves that let opponent reach/contest sooner, avoid getting too close to opponent.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # If opponent could contest soon, prioritize stealing/denying by maximizing our advantage growth.
        adv_next = nod - nsd
        opp_next = cheb(nx, ny, ox, oy)
        # Slight bias to reduce distance overall; deterministic tie-break handled at end.
        score = 1000 * adv_next + 5 * (cur_sd - nsd) - 2 * (1 if opp_next == 0 else 0) - 0.1 * opp_next
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]