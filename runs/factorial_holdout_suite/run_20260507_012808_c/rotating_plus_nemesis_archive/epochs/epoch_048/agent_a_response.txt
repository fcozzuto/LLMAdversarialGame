def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    free_targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                free_targets.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def best_target_from(posx, posy):
        # Maximize (opp_dist - self_dist) so we race to resources we can reach first.
        # Tie-break: smaller self_dist, then smaller lexicographic (x,y) for determinism.
        best = None
        best_key = None
        for tx, ty in free_targets:
            sd = cheb(posx, posy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            key = (od - sd, -sd, -tx, -ty)
            if best_key is None or key > best_key:
                best_key = key
                best = (tx, ty)
        return best

    # If no visible resources, move toward the nearest free cell from our side (avoid being stuck).
    if not free_targets:
        best_move = [0, 0]
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            key = (-cheb(nx, ny, ox, oy), nx, ny)
            if best_key is None or key > best_key:
                best_key = key
                best_move = [dx, dy]
        return best_move

    target = best_target_from(sx, sy)
    tx, ty = target

    # Prefer direct step toward target; if blocked, choose best safe move by same race metric.
    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)
    if valid(sx + desired_dx, sy + desired_dy):
        return [desired_dx, desired_dy]

    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        t2 = best_target_from(nx, ny)
        if t2 is None:
            key = (-cheb(nx, ny, ox, oy), nx, ny)
        else:
            sd = cheb(nx, ny, t2[0], t2[1])
            od = cheb(ox, oy, t2[0], t2[1])
            key = (od - sd, -sd, -t2[0], -t2[1], nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move