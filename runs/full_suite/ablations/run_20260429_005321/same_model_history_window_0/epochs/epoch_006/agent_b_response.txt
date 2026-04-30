def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    # Pick a resource where we can arrive earlier than opponent (maximize dist_opp - dist_self).
    best_r = None
    best_adv = -10**9
    best_sd = 10**9
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        if adv > best_adv or (adv == best_adv and sd < best_sd):
            best_adv = adv
            best_sd = sd
            best_r = (rx, ry)

    # If no resources visible, just move to increase distance from opponent while avoiding obstacles.
    if best_r is None:
        best = None
        best_score = -10**9
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            score = cheb(nx, ny, ox, oy)
            if score > best_score:
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]]

    rx, ry = best_r

    # Score candidate moves: get closer to chosen resource, keep some distance from opponent, avoid stepping into blocked lanes.
    best = None
    best_score = -10**18
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        d_self = cheb(nx, ny, rx, ry)
        d_opp = cheb(nx, ny, ox, oy)

        # Encourage moves that maintain/extend advantage.
        d_self_now = cheb(sx, sy, rx, ry)
        d_opp_now = cheb(ox, oy, rx, ry)
        cur_adv = d_opp_now - d_self_now
        new_adv = d_opp_now - d_self

        # If we become too close to opponent, penalize; otherwise slightly reward.
        score = (-2 * d_self) + (0.6 * d_opp) + (3.0 * (new_adv - cur_adv))

        # Small deterministic bias toward reducing x then y to break ties.
        score += -0.01 * abs((nx) - rx) - 0.005 * abs((ny) - ry)

        if score > best_score:
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]]