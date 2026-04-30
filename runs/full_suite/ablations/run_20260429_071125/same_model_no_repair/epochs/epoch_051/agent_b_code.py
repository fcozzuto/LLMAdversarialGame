def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_val = -10**18

    if not resources:
        return [0, 0]

    # Deterministic resource ordering: closest to opponent, then by coordinates.
    def res_key(r):
        rx, ry = r
        return (cheb(ox, oy, rx, ry), rx, ry)

    res_sorted = sorted(resources, key=res_key)
    # Keep a small set to stay fast and deterministic.
    top = res_sorted[:6] if len(res_sorted) > 6 else res_sorted

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        for rx, ry in top:
            if (rx, ry) in obstacles:
                continue
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            # Big reward if we are on a resource.
            if myd == 0:
                val += 10_000_000

            # Prefer states where we are closer than opponent.
            # advantage>0 => we are relatively nearer (good).
            advantage = opd - myd
            val += advantage * (200 // (myd + 1))

            # Strongly discourage moves that hand the nearest contested target to opponent.
            # (approx: if opponent can reach much sooner than us, penalize).
            if opd + 1 < myd:
                val -= (myd - opd) * 500

            # Light bias to move toward the "most contested" targets (smallest opponent distance).
            val += (12 - cheb(ox, oy, rx, ry)) * (5 // (myd + 1))

        # Secondary tie-break: keep closer to opponent corner for eventual control.
        val -= cheb(nx, ny, ox, oy) // 10

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best