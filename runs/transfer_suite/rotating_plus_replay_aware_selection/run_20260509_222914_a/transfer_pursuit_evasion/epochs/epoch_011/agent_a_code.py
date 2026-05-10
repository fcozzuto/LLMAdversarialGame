def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                res.append((rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def step_free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist_cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    opp_toward = True
    scores = observation.get("scores") or {}
    if "opponent_score" in scores and "self_score" in scores:
        try:
            opp_toward = scores["opponent_score"] <= scores["self_score"]
        except:
            opp_toward = True

    best = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not step_free(nx, ny):
            continue

        if res:
            # Go to nearest resource (slightly prefer those far from opponent)
            dres = min(dist_cheb(nx, ny, rx, ry) for rx, ry in res)
            dop = dist_cheb(nx, ny, ox, oy)
            val = dres * 10 - dop * 2
        else:
            # No visible resources: either approach or keep distance deterministically
            dop = dist_cheb(nx, ny, ox, oy)
            val = dop if opp_toward else -dop

        if best_val is None or val < best_val:
            best_val = val
            best = [dx, dy]

    return [int(best[0]), int(best[1])]