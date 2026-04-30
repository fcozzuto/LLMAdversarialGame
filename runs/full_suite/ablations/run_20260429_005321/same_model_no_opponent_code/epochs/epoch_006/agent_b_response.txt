def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]

    obst = {(p[0], p[1]) for p in obstacles}
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(a, b): return 0 <= a < w and 0 <= b < h
    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # If we're adjacent, prioritize escape from opponent.
    if d2(x, y, ox, oy) <= 2:
        best = (None, -10**18)
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obst: 
                continue
            val = d2(nx, ny, ox, oy)
            if val > best[1]: best = ((dx, dy), val)
        if best[0] is not None: return [best[0][0], best[0][1]]

    # Pick a target resource where we have the strongest reach advantage.
    if resources:
        best = (None, -10**18)
        for rx, ry in resources:
            md = d2(x, y, rx, ry)
            od = d2(ox, oy, rx, ry)
            if od <= md:  # avoid chasing resources opponent is at least as close to
                continue
            # Slightly prefer nearer resources among those.
            val = (od - md) - 0.01 * md
            if val > best[1]: best = ((rx, ry), val)
        if best[0] is None:
            # Fallback: pick resource with maximum (od-md) even if not dominant.
            best = (None, -10**18)
            for rx, ry in resources:
                md = d2(x, y, rx, ry)
                od = d2(ox, oy, rx, ry)
                val = (od - md) - 0.001 * (md + od)
                if val > best[1]: best = ((rx, ry), val)
        tx, ty = best[0]
    else:
        tx, ty = w // 2, h // 2

    # Evaluate moves: approach target, maintain distance from opponent, and avoid obstacles adjacency.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        md = d2(nx, ny, tx, ty)
        od = d2(nx, ny, ox, oy)

        # Obstacle adjacency penalty: discourage moving next to many obstacles.
        neigh = 0
        for adx, ady in deltas:
            px, py = nx + adx, ny + ady
            if inb(px, py) and (px, py) in obst:
                neigh += 1
        val = (-md) + 0.35 * od - 0.15 * neigh

        # If opponent could move onto target vicinity, slightly prefer staying less predictable near them.
        if resources:
            # discourage being too close to opponent while also not making target progress
            if od <= 4 and md >= d2(x, y, tx, ty):
                val -= 5.0

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]