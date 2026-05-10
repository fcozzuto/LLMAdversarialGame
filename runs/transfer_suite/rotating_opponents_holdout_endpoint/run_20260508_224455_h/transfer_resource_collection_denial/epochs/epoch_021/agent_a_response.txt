def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Prefer moves that keep us nearer while also denying opponent by picking resources
    # where opponent is currently close (most likely to be contested).
    res_sorted = sorted(resources, key=lambda p: (p[0], p[1]))

    def eval_resource(rx, ry, nx, ny):
        sd = man(nx, ny, rx, ry)
        od = man(ox, oy, rx, ry)
        # If we can beat opponent's current reach, good; else lower weight.
        reach_score = (od - sd)
        # Bonus if opponent is very close to this resource right now.
        opp_pressure = 16 - od
        if opp_pressure < 0:
            opp_pressure = 0
        return reach_score * 10 + opp_pressure * 3 - sd

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    order_bias = {(dx, dy): i for i, (dx, dy) in enumerate(moves)}

    best_move = (0, 0)
    best_sc = -10**18

    # If we're on/near an obstacle edge, consider local obstacle-avoidance deterministically.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        local_obs_pen = 0
        # Penalize moves that get us adjacent to obstacles (unless it helps contest strongly).
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                ax, ay = nx + adx, ny + ady
                if inb(ax, ay) and (ax, ay) in obstacles:
                    local_obs_pen += 2

        # Choose best contested resource after this move.
        sc = -local_obs_pen * 1.5
        for rx, ry in res_sorted:
            sd0 = man(sx, sy, rx, ry)
            sd = man(nx, ny, rx, ry)
            # Encourage progress toward resources we haven't already "committed" to.
            progress = sd0 - sd
            sc += eval_resource(rx, ry, nx, ny) + progress * 2

        # Deterministic tie-break: fixed move ordering
        sc = sc * 100 - order_bias[(dx, dy)]

        if sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]