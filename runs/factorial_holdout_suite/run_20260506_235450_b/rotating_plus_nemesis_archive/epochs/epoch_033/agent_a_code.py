def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = r[0], r[1]
            if (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    moves = [(dx, dy) for dx, dy in dirs if valid(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    # Choose a target resource where we are ahead or can take the lead quickly.
    best = None  # (score, tie, target, first_step)
    turns_left = observation.get("turns_remaining", 999)

    # Deterministic ordering to break ties: sort by x,y
    resources_sorted = sorted(resources)
    for rx, ry in resources_sorted:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # lead margin; if opponent is strictly closer, penalize heavily
        margin = ds - do
        # if we can reach and deny before opponent, prioritize
        reach_self = (ds <= turns_left)
        reach_opp = (do <= turns_left)
        if not reach_self and reach_opp:
            continue
        # smaller ds better, smaller margin (negative) better
        # score: prefer lead, then closeness, then potential (favor nearer resources overall)
        lead_bonus = 20 if margin <= 0 else 0
        catch_bonus = 10 if (margin > 0 and (margin <= 2)) else 0
        penal = (margin * 6) if margin > 0 else (abs(margin) * -1)
        proximity = -ds
        time_factor = -(ds // 3)
        # if opponent can also reach sooner, discourage
        opp_adv_pen = (8 if (do < ds) and reach_opp else 0)
        score = lead_bonus + catch_bonus + proximity + time_factor + penal - opp_adv_pen
        if best is None or (score, -rx, -ry) > best[0:3]:
            best = (score, -rx, -ry, (rx, ry))

    rx, ry = best[3]

    # Pick the move that minimizes our distance to (rx,ry) while staying away from obstacles and local traps.
    # Also avoid stepping into a square where opponent becomes strictly closer to the chosen target.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        ds2 = cheb(nx, ny, rx, ry)
        do2 = cheb(ox, oy, rx, ry)  # opponent position unchanged this turn in our model
        # local penalty: moving into squares adjacent to obstacles
        adj_obs = 0
        for ax, ay in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            tx, ty = nx + ax, ny + ay
            if (tx, ty) in obstacles:
                adj_obs += 1
        # discourage giving up lead
        give = 5 if (do2 < ds2) else 0
        # deterministic tie-break: larger x then y preferred
        val = (-ds2, adj_obs, give, -nx, -ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]