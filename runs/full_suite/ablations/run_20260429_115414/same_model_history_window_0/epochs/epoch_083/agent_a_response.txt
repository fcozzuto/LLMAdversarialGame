def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal_moves_from(x, y):
        moves = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if dx == 0 and dy == 0:
                    ok = True
                else:
                    ok = inb(nx, ny) and (nx, ny) not in obstacles
                if ok:
                    moves.append((dx, dy, nx, ny))
        return moves

    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer targets closer to us and farther from opponent.
            val = (do - ds) * 2.0 - ds
            if best is None or val > best[0]:
                best = (val, rx, ry)
        _, tx, ty = best
    else:
        # No resources: move to center-ish deterministically.
        tx, ty = w // 2, h // 2

    moves = legal_moves_from(sx, sy)

    # If standing on a resource, stay unless a move is clearly better.
    stay_score = -cheb(sx, sy, tx, ty)
    best_move = (0, 0, sx, sy)
    best_score = stay_score

    for dx, dy, nx, ny in moves:
        # If resource is on the destination, strongly prefer it.
        res_bonus = 0.0
        if (nx, ny) in set(tuple(p) for p in resources):
            res_bonus = 10.0
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # Also encourage moving away from opponent a bit.
        opp_dist = cheb(nx, ny, ox, oy)
        score = res_bonus - d_self + 0.35 * (d_opp - d_self) + 0.01 * opp_dist
        if score > best_score:
            best_score = score
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]