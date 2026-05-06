def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def legal_moves(px, py):
        out = []
        for dx, dy in deltas:
            nx, ny = px + dx, py + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                out.append((nx, ny))
        if not out:
            return [(px, py)]
        return out

    opp_next_positions = legal_moves(ox, oy)
    my_next_positions = legal_moves(sx, sy)

    # For each resource, estimate opponent's best 1-step distance to contest it.
    opp_best = {}
    for rx, ry in res:
        br = 10**9
        for ax, ay in opp_next_positions:
            d = dist((ax, ay), (rx, ry))
            if d < br:
                br = d
        opp_best[(rx, ry)] = br

    best_move = (0, 0)
    best_score = -10**18
    # Choose move that maximizes number of resources we are strictly closer to after 1 step,
    # breaking ties by smaller distance to those resources and by reducing opponent advantage.
    for nx, ny in my_next_positions:
        score = 0
        for rx, ry in res:
            sd = dist((nx, ny), (rx, ry))
            od = opp_best[(rx, ry)]
            if sd < od:
                score += 1000 - sd
            elif sd == od:
                score += 5 - sd
            else:
                score -= 2 * (sd - od)
        # Slight preference for moving toward center to avoid being trapped by obstacles.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score += -0.1 * (abs(nx - cx) + abs(ny - cy))
        if score > best_score:
            best_score = score
            best_move = (nx - sx, ny - sy)

    dx, dy = best_move
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]