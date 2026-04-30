def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Focus on likely targets: closest in Manhattan to opponent (to model their greedy approach).
    res_sorted = sorted(resources, key=lambda r: man(ox, oy, r[0], r[1]))
    candidates = res_sorted[:4] if len(res_sorted) > 4 else res_sorted

    best_move = (0, 0, sx, sy)
    best_val = -10**18
    for dx, dy, nx, ny in legal:
        val = 0
        for rx, ry in candidates:
            if (rx, ry) in obstacles:
                continue
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd == 0:
                val += 2_000_000
            else:
                # Voronoi-style: strongly prefer resources where we are not worse.
                # If we're worse, still try to reduce the gap (deny opponent progress).
                gap = opd - myd
                if myd <= opd:
                    val += (50 + gap * 60) // (myd + 1)
                else:
                    val -= (30 + (-gap) * 40) // (myd + 1)
                # Slight preference for moving closer overall to reduce our distance.
                val += 6 // (myd + 1)
        # Tie-break: avoid drifting away from the nearest candidate by opponent
        ax, ay = candidates[0]
        val -= man(nx, ny, ax, ay) * 0.01
        if val > best_val:
            best_val = val
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]