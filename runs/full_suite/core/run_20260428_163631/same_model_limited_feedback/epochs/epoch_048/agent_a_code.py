def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    moves = [(dx, dy) for dx, dy in moves if dx in (-1,0,1) and dy in (-1,0,1)]

    if not resources:
        best = (0,0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            d_self = abs(nx - ox) + abs(ny - oy)
            v = d_self
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Target resources by maximizing relative advantage: (opp_dist - self_dist)
    opp = (ox, oy)
    best_res = resources[0]
    best_adv = -10**9
    for rx, ry in resources:
        adv = dist((rx, ry), opp) - dist((rx, ry), (sx, sy))
        if adv > best_adv:
            best_adv = adv
            best_res = (rx, ry)

    tx, ty = best_res
    # Choose move that reduces self distance to target while keeping safer relative pressure
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        d_after = abs(nx - tx) + abs(ny - ty)
        d_now = abs(sx - tx) + abs(sy - ty)
        opp_d = abs(ox - tx) + abs(oy - ty)
        # Encourage going to target, avoid increasing distance, and slightly prefer moves that keep opponent worse
        score = (d_now - d_after) * 10 - d_after - (opp_d - (abs(nx - tx) + abs(ny - ty)))
        # Extra penalty for stepping near opponent (discourage being easy to capture/block)
        score -= (abs(nx - ox) + abs(ny - oy)) * 0.1
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]