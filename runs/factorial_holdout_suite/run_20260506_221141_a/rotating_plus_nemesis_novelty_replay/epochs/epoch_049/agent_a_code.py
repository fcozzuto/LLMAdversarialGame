def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_t = None
    best_key = (-10**18, 10**18, 10**18)  # adv desc, myd asc, tie x,y asc

    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        adv = opd - myd
        key = (adv, -myd, tx, ty)  # primary adv, then prefer smaller myd via -myd, deterministic tx/ty
        if key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t

    # pick best move among valid ones: maximize capture advantage, then reduce distance
    best_move = (0, 0)
    best_move_key = (-10**18, 10**18, 10**18)  # adv next desc, dist asc, deterministic
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        adv2 = opd2 - myd2
        key = (adv2, myd2, nx + 100 * ny)
        if key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]