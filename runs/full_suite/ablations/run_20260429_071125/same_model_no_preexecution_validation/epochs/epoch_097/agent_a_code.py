def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a deterministic target: maximize advantage (opponent farther than me); otherwise minimize my distance.
    if resources:
        best = None
        best_adv = -10**18
        best_ds = 10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if adv > best_adv or (adv == best_adv and (ds < best_ds or (ds == best_ds and (rx, ry) < best))):
                best_adv, best_ds, best = adv, ds, (rx, ry)
        tx, ty = best
    else:
        tx, ty = ox, oy  # no resources: drift toward opponent to contest/deny

    # One-step lookahead scoring
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(nx, ny, ox, oy)

        on_res = 1 if (nx, ny) in set(resources) else 0
        # If we can capture now, take it.
        score = -2.5 * myd + 0.15 * opd + (1000.0 if on_res else 0.0)

        # Prefer moves that keep/extend lead against opponent for the target.
        my_next = myd
        opp_next = cheb(ox, oy, tx, ty)
        score += 0.3 * (opp_next - my_next)

        # Deterministic tie-breaker on move.
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]