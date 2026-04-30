def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    res = observation["resources"]

    occ = set()
    for p in obstacles:
        occ.add((p[0], p[1]))
    best = None
    # Pick a target resource that maximizes advantage (opponent farther than us)
    for r in res:
        rx, ry = r[0], r[1]
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(oy - ry)
        adv = do - ds
        if best is None or adv > best[0] or (adv == best[0] and ds < best[1]):
            best = (adv, ds, rx, ry)
    if best is None:
        return [0, 0]
    tx, ty = best[2], best[3]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # If very close to opponent, prefer stepping away to avoid contesting collision/blocks
    opp_close = (max(abs(ox - sx), abs(oy - sy)) <= 1)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = (10**9, 10**9, 0, 0)  # score, tie, dx, dy
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in occ:
            continue
        d_self = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(ox - nx) + abs(oy - ny)
        # Primary: get closer to target; Secondary: avoid obstacles already handled
        score = d_self
        tie = 0
        # If opponent is adjacent, prioritize increasing distance from opponent
        if opp_close:
            score = (d_self * 10) - d_opp
            tie = -d_opp
        # Deterministic tie-breaker: prefer fewer dx magnitude, then dx, then dy
        mag = abs(dx) + abs(dy)
        if score < best_move[0] or (score == best_move[0] and (mag < best_move[1] or (mag == best_move[1] and (dx, dy) < (best_move[2], best_move[3])))):
            best_move = (score, mag, dx, dy)

    # If all moves blocked, stay (engine keeps in place)
    return [best_move[2], best_move[3]]