def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    if w <= 0 or h <= 0:
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18

    # Prefer grabbing resources we can get first; if tied, favor moves that also increase distance from opponent.
    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue

        val = 0
        # If we are at a resource, strongly prefer staying/collecting it.
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_own = cheb(nsx, nsy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Base: go closer (negative distance)
            # Bonus: being closer than opponent matters more for resource_denier
            # Bonus: prioritize immediate collection
            if d_own == 0:
                val += 10000
            val += -2 * d_own
            val += 4 * (d_opp - d_own)
        # Small penalty for moves that bring us closer to opponent (denial prevention)
        # but don't overreact if no resources.
        if resources:
            val -= 0.3 * cheb(nsx, nsy, ox, oy)

        if val > best_val:
            best_val = val
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]