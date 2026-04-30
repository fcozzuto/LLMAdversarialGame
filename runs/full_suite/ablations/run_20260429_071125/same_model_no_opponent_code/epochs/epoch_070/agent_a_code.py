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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    adj_opp = cheb(sx, sy, ox, oy) <= 1
    best_move = (0, 0)
    best_score = -10**18

    # Choose among moves by maximizing advantage over opponent on best available resource.
    # Score = (opp_closer_bonus) + resource_progress - risk_of_being_adjacent_to_opp - obstacle_penalty(handled by ok()).
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd_opp = cheb(nx, ny, ox, oy)
        risk = 10 if adj_opp and myd_opp <= 1 else 0

        if resources:
            best_res_score = -10**18
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Prefer resources where we are currently closer than opponent after this move.
                adv = (do - ds)  # positive is good
                # Tie-break: prefer moving closer overall, with mild bias for nearer resources.
                progress = -ds
                cand = adv * 4 + progress
                if cand > best_res_score:
                    best_res_score = cand
            score = best_res_score - risk
        else:
            # No resources known: just increase separation.
            score = myd_opp - risk

        # Deterministic tie-break: prefer lexicographically smaller (dx,dy) among equal scores.
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]