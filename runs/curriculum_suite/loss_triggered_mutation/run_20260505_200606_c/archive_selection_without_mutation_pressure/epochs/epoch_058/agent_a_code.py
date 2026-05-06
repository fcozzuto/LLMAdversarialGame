def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_target = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        # Prefer secure/tie grabs; otherwise race for least-losing.
        key = (-(adv >= 0), -adv, sd, -(od), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)
    if best_target is None:
        best_target = resources[0]
    rx, ry = best_target

    # One-step lookahead: maximize advantage toward chosen target; slight tie-break to avoid giving opponent faster access.
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = cheb(nx, ny, rx, ry)
        nod = cheb(ox, oy, rx, ry)
        adv = nod - nsd
        # Extra: if multiple resources remain, bias toward moving closer to the best overall resource from next position.
        # Keep deterministic and cheap: only compare against current best_target and one nearest other resource.
        nearest = None
        nearest_d = None
        for ex, ey in resources:
            if (ex, ey) in obstacles:
                continue
            d = cheb(nx, ny, ex, ey)
            if nearest_d is None or d < nearest_d:
                nearest_d = d
                nearest = (ex, ey)
        nxd = nearest_d if nearest is not None else 0
        key = (-(adv >= 0), -adv, nxd, cheb(ox, oy, rx, ry) - cheb(ox, oy, nearest[0], nearest[1]) if nearest else 0, dx, dy)
        if best_mkey is None or key < best_mkey:
            best_mkey = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]