def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [(w // 2, h // 2)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Target: maximize advantage (opp_dist - self_dist); tie-break by absolute closeness.
    best_tx, best_ty = resources[0]
    best_adv = -10**9
    best_sum = 10**9
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - sd
        s = sd + od
        if adv > best_adv or (adv == best_adv and s < best_sum):
            best_adv, best_sum = adv, s
            best_tx, best_ty = tx, ty

    cur_to_t = cheb(sx, sy, best_tx, best_ty)
    cur_agents = cheb(sx, sy, ox, oy)

    # Next move: greedily reduce distance to target; avoid squares that let opponent get strictly closer too easily.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, best_tx, best_ty)
        if nd > cur_to_t + 1:  # avoid drifting away
            continue
        nod = cheb(ox, oy, best_tx, best_ty)
        # opponent closeness to us (lower is worse)
        agents = cheb(nx, ny, ox, oy)
        # estimate who would be closer to target after move
        self_after = nd
        opp_after = nod
        steal_risk = 0
        if opp_after <= self_after:  # opponent at least as close
            steal_risk = 2
        # Score: prioritize distance drop, then keep distance between agents, then reduce steal risk.
        score = (cur_to_t - nd) * 100 - nd * 2 + agents - steal_risk * 50
        # deterministic tie-break: prefer moves closer to (1,0),(0,1),(-1,0),(0,-1) ordering using fixed list index
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]