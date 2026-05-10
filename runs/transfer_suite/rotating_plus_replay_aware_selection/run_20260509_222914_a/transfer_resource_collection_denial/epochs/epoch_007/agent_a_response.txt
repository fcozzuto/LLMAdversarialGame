def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def cheb(a, b, c, d):
        da = abs(a - c)
        db = abs(b - d)
        return da if da > db else db

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            sd = cheb(x, y, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            key = (-(adv), sd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    if (x, y) not in obstacles:
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        cand = (x + dx, y + dy)
        if 0 <= cand[0] < w and 0 <= cand[1] < h and cand not in obstacles:
            return [dx, dy]

    # Pick best safe move toward target; deterministic tie-break using deltas order.
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist_to = cheb(nx, ny, tx, ty)
        dist_opp = cheb(nx, ny, ox, oy)
        # Primary: get closer to target, secondary: avoid moving into opponent (sweep mitigation).
        score = (dist_to, -dist_opp, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move