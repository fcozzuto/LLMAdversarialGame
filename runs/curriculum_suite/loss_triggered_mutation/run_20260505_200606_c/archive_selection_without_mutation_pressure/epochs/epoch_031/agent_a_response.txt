def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obs = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def best_for(posx, posy, target_list):
        bestd = 10**9
        best = None
        for rx, ry in target_list:
            d = dist(posx, posy, rx, ry)
            if d < bestd:
                bestd = d
                best = (rx, ry)
        return bestd, best

    opp_near_d, opp_target = best_for(ox, oy, resources)
    our_near_d, our_target = best_for(sx, sy, resources)
    # If we can't see a clear target, just head to nearest.
    if opp_target is None:
        t = our_target
        tx, ty = t
        step = [0, 0]
        if tx > sx:
            step[0] = 1
        elif tx < sx:
            step[0] = -1
        if ty > sy:
            step[1] = 1
        elif ty < sy:
            step[1] = -1
        return [step[0], step[1]]

    txo, tyo = opp_target
    txu, tyu = our_target

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        # Our advantage: improve closeness to our nearest target while reducing opponent's closeness.
        our_d = dist(nx, ny, txu, tyu)
        opp_d_next = dist(nx, ny, txo, tyo)  # proxy for interference on their current best target
        # Also consider overall best resource for each side.
        our_best_d, _ = best_for(nx, ny, resources)

        # Blocking bias: align y with opponent's target row to contest the same sweep.
        y_align = -abs(ny - tyo)

        # Score: smaller distances are better. Opp interference wants us closer to opp's target than they are.
        score = 0
        score += (our_near_d - our_best_d) * 10
        score += (opp_near_d - opp_d_next) * 6
        score += y_align * 2

        # Mild tie-break: prefer moving toward our target.
        score += -dist(nx, ny, txu, tyu) * 0.01

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]