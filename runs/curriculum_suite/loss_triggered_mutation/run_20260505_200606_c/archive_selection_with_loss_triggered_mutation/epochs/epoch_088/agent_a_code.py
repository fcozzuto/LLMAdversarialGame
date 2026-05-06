def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        moves = [(-1, 1), (0, 1), (1, 1), (-1, 0), (0, 0), (1, 0), (-1, -1), (0, -1), (1, -1)]
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # keep distance from opponent a bit
            obj = -man(nx, ny, ox, oy)
            if obj < best[0]:
                best = (obj, dx, dy)
        return [best[1], best[2]]

    moves = [(-1, 1), (0, 1), (1, 1), (-1, 0), (0, 0), (1, 0), (-1, -1), (0, -1), (1, -1)]
    best_move = [0, 0]
    best_obj = 10**18

    # Precompute resource list as ints
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Prefer resources we can reach earlier and that are far from opponent
        best_res_obj = 10**18
        for rx, ry in res:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # lower is better: small sd, large od
            obj = sd - 2.0 * od + 0.15 * man(nx, ny, ox, oy)
            if obj < best_res_obj:
                best_res_obj = obj

        # If no resource seems good (shouldn't happen), fall back to maximizing distance from opponent
        if best_res_obj == 10**18:
            best_res_obj = man(nx, ny, ox, oy)

        # Deterministic tie-break: fixed move order by iteration already
        if best_res_obj < best_obj:
            best_obj = best_res_obj
            best_move = [dx, dy]

    return best_move