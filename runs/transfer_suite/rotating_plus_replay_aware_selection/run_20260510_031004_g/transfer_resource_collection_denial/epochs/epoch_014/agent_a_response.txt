def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    res = [(int(p[0]), int(p[1])) for p in resources]
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate move by resulting advantage over all resources.
        best_adv = None
        best_tgt_myd = None
        for tx, ty in res:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            adv = opd - myd
            # prefer immediate capture likelihood, then advantage, then closeness
            key = (adv, -(myd), -(tx + ty))
            if best_adv is None or key > best_adv:
                best_adv = key
                best_tgt_myd = myd

        if best_adv is None:
            continue

        # If we have strict winning chances, heavily prefer those moves.
        has_win = best_adv[0] >= 1
        win_bonus = 10000 if has_win else 0

        # Also consider not letting opponent get closer by tracking my distance to their closest target.
        opd_closest = None
        for tx, ty in res:
            opd = cheb(ox, oy, tx, ty)
            if opd_closest is None or opd < opd_closest:
                opd_closest = opd
        # lower my distance to that same closest resource helps block; approximate by min myd among resources with opd==opd_closest
        block_myd = None
        for tx, ty in res:
            if cheb(ox, oy, tx, ty) == opd_closest:
                myd = cheb(nx, ny, tx, ty)
                if block_myd is None or myd < block_myd:
                    block_myd = myd
        if block_myd is None:
            block_myd = best_tgt_myd

        score = win_bonus + best_adv[0] * 500 - best_tgt_myd * 2 - block_myd
        # Deterministic tie-break: lexicographic by target direction bias
        tie = (-(dx), -(dy), nx, ny)
        item = (score, tie)
        if best is None or item > best:
            best = item
            best_move = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]