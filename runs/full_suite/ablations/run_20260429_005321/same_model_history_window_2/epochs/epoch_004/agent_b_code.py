def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def best_move_toward(nx, ny):
        if not resources:
            cx, cy = w // 2, h // 2
            best = [0, 0]
            best_sc = -10**18
            for dx, dy in deltas:
                tx, ty = nx + dx, ny + dy
                if not inb(tx, ty) or (tx, ty) in obstacles:
                    continue
                dcen = manh(tx, ty, cx, cy)
                oppd = cheb(tx, ty, ox, oy)
                sc = -dcen - 0.02 * oppd
                if sc > best_sc:
                    best_sc = sc
                    best = [dx, dy]
            return best

        # Choose the resource where we can arrive no later than opponent (or at least contest strongly).
        best_dxdy = [0, 0]
        best_key = (-10**18, -10**18, -10**18)
        for dx, dy in deltas:
            tx, ty = nx + dx, ny + dy
            if not inb(tx, ty) or (tx, ty) in obstacles:
                continue

            # Evaluate this candidate cell against a single best resource.
            best_r = None
            best_r_key = None
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                myd = manh(tx, ty, rx, ry)
                opd = manh(ox, oy, rx, ry)
                # Want minimal time for self; strongly prefer resources we can beat or at least contest.
                # Tie-break deterministically by position.
                k = (-myd, -(myd - opd), -cheb(tx, ty, ox, oy), -rx - 100 * ry)
                if best_r_key is None or k > best_r_key:
                    best_r_key = k
                    best_r = (rx, ry)
            if best_r_key is None:
                continue

            rx, ry = best_r
            myd = manh(tx, ty, rx, ry)
            opd = manh(ox, oy, rx, ry)
            contest_bonus = 1.0 if myd <= opd else 0.0
            # Overall key: prefer beating opponent, then closer, then farther from opponent.
            key = (contest_bonus, -myd, myd - opd)
            if key > best_key:
                best_key = key
                best_dxdy = [dx, dy]
        return best_dxdy

    # Compute direct candidate move from current position.
    return best_move_toward(sx, sy)