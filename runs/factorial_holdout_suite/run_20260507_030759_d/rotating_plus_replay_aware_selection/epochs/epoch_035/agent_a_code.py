def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_dxdy = [0, 0]
    best_score = -10**18
    best_secondary = 10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        best_for_move = -10**18
        closest_self = 10**9
        closest_opp = 10**9

        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            if ds < closest_self:
                closest_self = ds
            if do < closest_opp:
                closest_opp = do

            # Advantage score: strongly prefer targets where we are closer; else minimize being behind.
            adv = do - ds
            # If we can reach immediately, prioritize it heavily.
            if ds == 0:
                score = 10**9 + (do - ds) * 1000
            else:
                # Reward winning races, and penalize losing races nonlinearly.
                # Normalize by distance so "nearby win" beats "far win".
                if adv > 0:
                    score = adv * 1000 - ds
                else:
                    score = adv * 200 + do * 5 + ds
            if score > best_for_move:
                best_for_move = score

        secondary = closest_self - 0.1 * closest_opp
        if best_for_move > best_score or (best_for_move == best_score and secondary < best_secondary):
            best_score = best_for_move
            best_secondary = secondary
            best_dxdy = [dx, dy]

    return best_dxdy