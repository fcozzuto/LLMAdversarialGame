def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    grid_w = observation.get("grid_width", 8)
    grid_h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < grid_w and 0 <= y < grid_h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Target selection changed: prioritize resources where we are already closer,
    # and among them, maximize opponent's distance (deterministic tie-break).
    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # primary: we want sd <= od, then minimize sd; secondary: maximize od
        sd_ok = 1 if sd <= od else 0
        key = (sd_ok, -od, -sd, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    rx, ry = best[1]

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # Choose best immediate move: reduce distance to target, avoid obstacles,
    # and (slightly) avoid giving opponent a closer approach to target.
    opp_target_dist = cheb(ox, oy, rx, ry)
    best_move = (None, None)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        my_d = cheb(nx, ny, rx, ry)
        # heuristic: if we can collect soon, also prefer staying on-resource line
        self_adv = opp_target_dist - my_d
        opp_if = cheb(ox, oy, rx, ry)  # opponent move unknown; keep simple deterministic term
        # Score: prioritize reaching, then maximizing advantage, then deterministic tie on position
        score = (-my_d, -self_adv, opp_target_dist - opp_if, nx, ny)
        if best_move[0] is None or score > best_move[0]:
            best_move = (score, [dx, dy])

    if best_move[1] is None:
        return [0, 0]
    return best_move[1]