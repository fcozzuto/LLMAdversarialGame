def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def blocked(x, y):
        return (x, y) in obs or not (0 <= x < w and 0 <= y < h)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    # Evaluate each move by the best "grab advantage" it enables next turn.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        # If we can take a resource immediately, do so.
        immediate = False
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = r[0], r[1]
                if isinstance(rx, int) and isinstance(ry, int) and rx == nx and ry == ny and not blocked(rx, ry):
                    immediate = True
                    break
        if immediate:
            return [dx, dy]

        # Choose resource that yields maximum advantage at next position.
        # Advantage = (opponent distance - our distance); larger is better.
        local_best_adv = None
        local_best_sd = None
        for r in resources:
            if not isinstance(r, (list, tuple)) or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if not (isinstance(rx, int) and isinstance(ry, int)):
                continue
            if blocked(rx, ry):
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if local_best_adv is None or adv > local_best_adv or (adv == local_best_adv and sd < local_best_sd):
                local_best_adv = adv
                local_best_sd = sd

        # Also break ties by favoring moves that improve our best distance (even if opponent is close).
        # Slightly weight positive advantage to beat opportunistic race losses.
        val = (local_best_adv is None and -10**9) or local_best_adv
        if local_best_adv is None:
            val = -10**9
            local_best_sd = 10**9
        key = (val, -local_best_sd, dx, dy)
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]