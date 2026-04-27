def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]
    if resources:
        best_adv = -10**9
        best_dself = 10**9
        target = None
        for rx, ry in resources:
            dself = cheb(sx, sy, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            adv = dop - dself
            if adv > best_adv or (adv == best_adv and dself < best_dself):
                best_adv = adv
                best_dself = dself
                target = (rx, ry)
        if best_adv < 0:
            # We are behind: switch to deny by heading for closest resource anyway
            target = min(resources, key=lambda p: cheb(sx, sy, p[0], p[1]))
    else:
        target = (w // 2, h // 2)
    # Choose move that maximizes progress to target, with slight opponent-avoidance.
    best = None
    best_score = -10**18
    for dx, dy, nx, ny in candidates:
        d_to_t = cheb(nx, ny, target[0], target[1])
        d_from_o = cheb(nx, ny, ox, oy)
        # If target is close, prioritize securing it; otherwise, keep distance from opponent.
        score = (-d_to_t * 10) + (d_from_o * 0.15)
        if resources:
            d_cur_t = cheb(sx, sy, target[0], target[1])
            if d_to_t < d_cur_t:
                score += 1.5
            elif d_to_t == d_cur_t:
                score -= 0.2
        if score > best_score:
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]]