def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        tx = 0 if ox > w - 1 - ox else (w - 1 if ox < (w - 1) // 2 else 0)
        # simpler deterministic: move to corner farthest from opponent
        farx = 0 if abs(0 - ox) >= abs(w - 1 - ox) else w - 1
        fary = 0 if abs(0 - oy) >= abs(h - 1 - oy) else h - 1
        dx = 0 if farx == sx else (1 if farx > sx else -1)
        dy = 0 if fary == sy else (1 if fary > sy else -1)
        return [dx, dy]

    res = [tuple(r) for r in resources]
    res.sort()  # deterministic

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = None
    best_score = -10**18

    opp_d_cache = {}
    for rx, ry in res:
        opp_d_cache[(rx, ry)] = dist(rx, ry, ox, oy)

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy

        # Race heuristic: prioritize resources we can become closer to than opponent
        # than their current advantage, favoring earlier pickup (lower our distance).
        local_best = -10**18
        local_tie = None
        for rx, ry in res:
            our_d = dist(nx, ny, rx, ry)
            opp_d = opp_d_cache[(rx, ry)]
            # If we land on a resource, immediately dominate.
            if our_d == 0:
                score = 10**12
            else:
                score = (opp_d - our_d) * 1000 - our_d
            if score > local_best:
                local_best = score
                local_tie = (rx, ry)
            elif score == local_best:
                if (rx, ry) < local_tie:
                    local_tie = (rx, ry)

        # Secondary: if two moves fight over same local_best, prefer safer progress (closer to best target)
        tx, ty = local_tie
        our_d_to_choice = dist(nx, ny, tx, ty)
        final_score = local_best - our_d_to_choice
        if final_score > best_score:
            best_score = final_score
            best_move = (dx, dy)
        elif final_score == best_score:
            if best_move is None or (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]