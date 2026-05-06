def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

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
    if not resources:
        return [0, 0]

    # Prefer targets where we can arrive closer than opponent (resource denial style).
    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine rejects; keep deterministic evaluation consistent

        # Compute best attainable value over all resources.
        val = -10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If opponent is already adjacent, avoid (likely to steal/deny).
            if do <= 1:
                continue
            # Main objective: maximize advantage in arrival time; small bonus for proximity.
            adv = do - ds
            score = adv * 10 - ds
            # If we can reach now, spike.
            if ds == 0:
                score = 10**6
            # Slight deterministic tie-break: favor upper-left resources.
            score += (-rx - ry) * 0.001
            if score > val:
                val = score

        # If all targets were skipped due to do<=1, just chase nearest while avoiding staying blocked.
        if val == -10**9:
            val = -min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        # Secondary tie-break: prefer moves that reduce our distance to the best resource.
        if best is None or val > best:
            best = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]