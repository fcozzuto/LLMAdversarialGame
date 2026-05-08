def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Identify opponent's likely target: nearest resource by Manhattan distance
    opp_target = min(resources, key=lambda r: (md(ox, oy, r[0], r[1]), r[0], r[1]))

    # Identify our target: resource where we are most likely to beat opponent (largest distance advantage)
    best = None
    best_adv = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        adv = od - sd
        if best_adv is None or adv > best_adv or (adv == best_adv and (sd < md(sx, sy, best[0], best[1]) if best else True)):
            best_adv = adv
            best = (rx, ry)
    tx, ty = best

    # Evaluate moves: primarily reduce our distance to our target; secondarily increase opponent distance to its target
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        myd = md(nx, ny, tx, ty)
        od_now = md(ox, oy, opp_target[0], opp_target[1])
        # We can't control opponent movement, but we can discourage them by reducing their future reach: move "away" from the corridor
        # Use a heuristic: if our move also increases distance between us and opponent target, it's less likely we collide and lose race.
        myd_opp = md(nx, ny, opp_target[0], opp_target[1])
        # Combine: smaller is better for myd; larger is better for myd_opp and (implicitly) future interference.
        key = (myd, -myd_opp, dx, dy, -od_now)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]