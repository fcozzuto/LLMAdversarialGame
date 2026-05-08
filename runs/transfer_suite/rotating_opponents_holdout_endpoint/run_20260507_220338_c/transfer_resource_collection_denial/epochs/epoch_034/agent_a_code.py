def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    valid_moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    res_list = [tuple(r) for r in resources if tuple(r) not in obstacles]
    if not res_list:
        return [0, 0]

    # Opponent baseline: how close they are to any remaining resource.
    opp_near = min(man(ox, oy, rx, ry) for rx, ry in res_list)

    best = (0, 0, -10**9)  # (dx,dy,score)
    for dx, dy in valid_moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_near = min(man(nx, ny, rx, ry) for rx, ry in res_list)

        # Contest/lead metric: best advantage over opponent among reachable resources.
        max_adv = -10**9
        for rx, ry in res_list:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            adv = opd - myd
            if adv > max_adv:
                max_adv = adv

        # Prefer increasing advantage and reducing opponent's relative closeness.
        # If opponent is closer (opp_near < my_near), this penalizes our move.
        rel_penalty = opp_near - my_near
        score = max_adv * 5 - rel_penalty

        if score > best[2]:
            best = (dx, dy, score)

    if best[2] < -10**8:
        return [0, 0]
    return [best[0], best[1]]