def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def md(ax, ay, bx, by):
        return max(abs(ax - bx), abs(ay - by))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    def adj_obs(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    p += 1
        return p

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        myd_to_opp = md(nx, ny, ox, oy)
        best_t = None
        best_key = None
        for tx, ty in resources:
            if (tx, ty) in obstacles:
                continue
            myd = md(nx, ny, tx, ty)
            opd = md(ox, oy, tx, ty)

            contest = 1 if myd <= opd else 0
            # If we're behind, strongly prefer targets that we can improve relative to opponent.
            rel = opd - myd
            key = (
                contest,
                rel,
                -myd,
                -(adj_obs(tx, ty)),
                # mild bias to targets not too far from the midpoint (reduces long races)
                -md(tx, ty, (w - 1) // 2, (h - 1) // 2),
            )
            if best_key is None or key > best_key:
                best_key = key
                best_t = (tx, ty)

        if best_t is None:
            continue

        # Prefer moves that also don't let opponent gain too much tempo (tie-breaker).
        tx, ty = best_t
        myd_final = md(nx, ny, tx, ty)
        opd_final = md(ox, oy, tx, ty)
        val = (
            (1 if myd_final <= opd_final else 0),
            (opd_final - myd_final),
            -myd_final,
            -myd_to_opp,
            -adj_obs(nx, ny),
        )

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]