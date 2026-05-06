def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    def cell_in(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # pick best resource: maximize opponent delay and my proximity (deterministic tiebreak)
    best = resources[0]
    best_tv = None
    for tx, ty in resources:
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        tv = (d_opp - d_me) * 1000 - d_me + (0.001 * d_opp)
        if best_tv is None or tv > best_tv or (tv == best_tv and (d_opp < (abs(best[0] - x) + abs(best[1] - y)))):
            best, best_tv = [tx, ty], tv
        elif tv == best_tv and (tx, ty) < (best[0], best[1]):
            best, best_tv = [tx, ty], tv
    tx, ty = best

    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    # evaluate candidate next steps
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not cell_in(nx, ny):
            continue
        my_d = abs(tx - nx) + abs(ty - ny)
        opp_d = abs(tx - ox) + abs(ty - oy)
        adv = (opp_d - (my_d))  # prefer cells that increase advantage
        # also slightly prefer reducing my distance; and avoid moving into opponent's vicinity
        opp_prox = -((abs(nx - ox) + abs(ny - oy)) if (abs(nx - ox) + abs(ny - oy)) > 0 else -1)
        score = adv * 1000 - my_d + 0.01 * opp_d + 0.001 * opp_prox
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score, best_move = score, (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]