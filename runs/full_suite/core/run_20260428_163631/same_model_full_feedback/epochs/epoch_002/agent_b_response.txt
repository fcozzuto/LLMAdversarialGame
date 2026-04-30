def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obs = set(map(tuple, observation.get("obstacles", [])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(a, b): 
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        tx = ox - sx
        ty = oy - sy
        dx = 0 if tx == 0 else (1 if tx > 0 else -1)
        dy = 0 if ty == 0 else (1 if ty > 0 else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [dx, dy]
        # deterministic fallback: move toward nearer corner-opponent line while avoiding obstacles
        best = [0, 0]
        bestv = -10**9
        for ddx, ddy in deltas:
            nx, ny = sx + ddx, sy + ddy
            if not inb(nx, ny) or (nx, ny) in obs: 
                continue
            v = -cheb((nx, ny), (ox, oy))
            if v > bestv:
                bestv = v; best = [ddx, ddy]
        return best

    # Target resource: maximize how much closer we are than opponent (or maximize their disadvantage)
    best_r = None
    best_adv = None
    for r in resources:
        rd = (r[0], r[1])
        sa = cheb((sx, sy), rd)
        oa = cheb((ox, oy), rd)
        adv = oa - sa  # higher => we are closer than opponent
        if best_adv is None or adv > best_adv or (adv == best_adv and (sa < cheb((sx, sy), best_r))):
            best_adv = adv
            best_r = rd

    tx, ty = best_r

    # Evaluate next move: prioritize improving our advantage for target, avoid letting opponent get closer
    cur_self_d = cheb((sx, sy), (tx, ty))
    cur_opp_d = cheb((ox, oy), (tx, ty))
    best_move = [0, 0]
    best_score = -10**18
    for ddx, ddy in deltas:
        nx, ny = sx + ddx, sy + ddy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nd_self = cheb((nx, ny), (tx, ty))
        nd_opp = cheb((ox, oy), (tx, ty))
        # Opponent d doesn't change this turn; but we can still take actions that likely contest by reducing our own d
        score = (cur_opp_d - nd_self) * 100
        # Small tie-breakers: prefer actually moving closer in true distance and avoid moving away
        score -= abs(nd_self - cur_self_d)
        # If we can capture the resource by stepping onto it, add large bonus
        if (nx, ny) == (tx, ty):
            score += 100000
        # Encourage reducing opponent's ability indirectly by keeping us close to target relative to baseline
        score += (cur_self_d - nd_self) * 3

        # Deterministic tie-break: lexicographic on move delta
        if score > best_score or (score == best_score and [ddx, ddy] < best_move):
            best_score = score
            best_move = [ddx, ddy]

    # If all moves blocked, stay (engine keeps us in place)
    return best_move