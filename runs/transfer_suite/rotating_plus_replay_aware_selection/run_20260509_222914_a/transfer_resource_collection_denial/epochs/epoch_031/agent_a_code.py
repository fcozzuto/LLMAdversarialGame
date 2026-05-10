def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    resset = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            res.append((px, py))
            resset.add((px, py))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_val = -10**18

    if res:
        my_near = min(dist((x, y), r) for r in res)
        op_near = min(dist((ox, oy), r) for r in res)
        base_lead = op_near - my_near  # positive: we are closer
    else:
        base_lead = 0

    for dx0, dy0 in deltas:
        nx, ny = x + dx0, y + dy0
        if not inb(nx, ny):
            nx, ny = x, y
        hit = (nx, ny) in resset

        if res:
            my_d = min(dist((nx, ny), r) for r in res)
            opp_d = min(dist((ox, oy), r) for r in res)
            lead = opp_d - my_d
            to_opp = dist((nx, ny), (ox, oy))
            val = (100000 if hit else 0) + 200 * lead + (my_near - my_d) - 3 * to_opp + base_lead
        else:
            # Drift toward center while keeping distance from opponent
            cx, cy = (w - 1) // 2, (h - 1) // 2
            to_center = dist((nx, ny), (cx, cy))
            to_opp = dist((nx, ny), (ox, oy))
            val = -to_center + 2 * to_opp

        if val > best_val:
            best_val = val
            best = [nx - x, ny - y]

    return [int(best[0]), int(best[1])]