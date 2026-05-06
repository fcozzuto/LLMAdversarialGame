def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick a resource that we are relatively better positioned for.
    best_r = resources[0]
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (do - ds, -ds)  # prefer resources where opponent is farther and we are closer
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    my_ahead = best_key[0] > 0  # positive means we are closer than opponent

    # If opponent is closer to the chosen target, prioritize distance from opponent (counter-patrol),
    # otherwise prioritize progress to the chosen target.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        ds_next = cheb(nx, ny, tx, ty)
        do_next = cheb(nx, ny, ox, oy)
        ds_now = cheb(sx, sy, tx, ty)
        do_now = cheb(sx, sy, ox, oy)

        if my_ahead:
            # go toward target, but don't let opponent gain a huge positional advantage
            score = (ds_now - ds_next) * 8.0 + do_next * 0.05 - ds_next * 0.02
        else:
            # opponent is closer: keep them off by increasing separation and only then progress
            score = do_next * 1.2 - ds_next * 0.3 + (do_next - do_now) * 0.5

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]