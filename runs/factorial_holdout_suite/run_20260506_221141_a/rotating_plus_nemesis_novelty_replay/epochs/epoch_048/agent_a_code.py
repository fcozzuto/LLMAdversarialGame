def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obs_set = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < gw and 0 <= py < gh:
                obs_set.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs_set:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obs_set

    best_target = None
    best_adv = -10**9
    best_tie = (10**9, 10**9)
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        adv = opd - myd  # positive means I'm closer
        tie = (myd, tx + ty)
        if adv > best_adv or (adv == best_adv and tie < best_tie):
            best_adv = adv
            best_tie = tie
            best_target = (tx, ty)
    tx, ty = best_target

    curd = cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        my_improve = curd - nd
        oppd = cheb(ox, oy, tx, ty)
        oppd_after = cheb(ox, oy, tx, ty)  # static opponent estimate (keeps determinism/simple)
        block = 0
        if best_adv > 0:
            block = 1  # encourage taking close targets
        val = my_improve * 100 + block - (oppd_after - oppd)  # tie-break handled below
        tie = (val, -nd, nx, ny)
        if tie[0] > best_val or (tie[0] == best_val and tie[1:] > best_move):
            best_val = tie[0]
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]