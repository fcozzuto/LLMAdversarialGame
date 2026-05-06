def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(tuple(p) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick a promising target: prefer resources where we are (currently) closer than opponent.
    best_res = None
    best_adv = -10**9
    best_myd = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        adv = oppd - myd
        # adv>0 means we are closer; tie-break deterministically by myd then position sum
        if adv > best_adv or (adv == best_adv and (best_myd is None or myd < best_myd)) or (adv == best_adv and myd == best_myd and best_res is not None and (rx + ry) < (best_res[0] + best_res[1])):
            best_adv = adv
            best_myd = myd
            best_res = (rx, ry)

    if best_res is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_res

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd = cheb(nx, ny, tx, ty)
        oppd = cheb(nx, ny, ox, oy)  # proxy for ability to contest
        # Evaluate denial pressure: how much closer we are to the target than opponent will be once they move (proxy).
        # Also reward reducing distance to target strongly.
        # For robustness, incorporate a small tie-break using coordinates.
        if best_res is not None:
            trd = cheb(nx, ny, tx, ty)
            ordd = cheb(ox, oy, tx, ty)
            denial = ordd - trd  # positive if we are closer than opponent currently
            score = 6 * denial - 2 * trd + 0.01 * (oppd)
        else:
            score = -2 * myd + 0.01 * (oppd)
        score -= 0.001 * (abs(nx - (w // 2)) + abs(ny - (h // 2)))
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]