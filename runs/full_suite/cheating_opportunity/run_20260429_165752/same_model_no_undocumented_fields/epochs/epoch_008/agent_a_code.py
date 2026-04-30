def choose_move(observation):
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for o in obstacles:
        try:
            obs_set.add((int(o[0]), int(o[1])))
        except Exception:
            pass

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    res_list = []
    for r in resources:
        try:
            res_list.append((int(r[0]), int(r[1])))
        except Exception:
            pass
    res_set = set(res_list)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if (x, y) in obs_set:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs_set:
                return [dx, dy]
        return [0, 0]

    if (x, y) in res_set:
        return [0, 0]

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        if (nx, ny) in res_set:
            return [dx, dy]
        if not res_list:
            best = [dx, dy]
            break

        # Evaluate: choose move maximizing (opponent distance - our distance) to the best target we can contest,
        # with tie-breaking toward smaller our distance.
        local_best = None
        for rx, ry in res_list:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Primary: contest advantage; Secondary: prefer being closer; Tertiary: deterministic tie-break by coords.
            key = (opp_d - our_d, -our_d, -rx, -ry)
            if local_best is None or key > local_best[0]:
                local_best = (key, our_d, opp_d)
        key = local_best[0]
        # Small penalty if move increases distance to all resources (discourage wandering).
        if key[1] is not None:
            pass
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best