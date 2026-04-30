def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        key = (adv, -sd, -rx, -ry)  # deterministic tie-break
        if best is None or key > best[0]:
            best = (key, rx, ry)
    if best is None:
        return [0, 0]
    _, tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_sd = cheb(sx, sy, tx, ty)
    opp_sd = cheb(ox, oy, tx, ty)

    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        # Prefer improving own distance; then improve advantage vs opponent.
        adv = opp_sd - nd
        dec = cur_sd - nd
        key = (dec, adv, -nd, dx, dy)
        if best_m is None or key > best_m[0]:
            best_m = (key, dx, dy)

    if best_m is None:
        return [0, 0]
    return [best_m[1], best_m[2]]