def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        best = (0, 10**9, (0, 0))
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
                if d > best[0]:
                    best = (d, 0, (dx, dy))
        return best[2]

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # Pick resource where we have the strongest reach advantage over opponent
    best_adv = -10**18
    best_dself = 10**18
    target = None
    for rx, ry in resources:
        d_self = dist2(sx, sy, rx, ry)
        d_opp = dist2(ox, oy, rx, ry)
        adv = d_opp - d_self
        if adv > best_adv or (adv == best_adv and d_self < best_dself):
            best_adv = adv
            best_dself = d_self
            target = (rx, ry)
    tx, ty = target

    # Move one step deterministically toward target, but avoid obstacles and discourage moving into opponent proximity
    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_t = dist2(nx, ny, tx, ty)
        d_to_o = dist2(nx, ny, ox, oy)
        # Prefer reducing distance to target; also prefer increasing distance from opponent when contesting
        score = (-d_to_t) + (0.15 * d_to_o)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]