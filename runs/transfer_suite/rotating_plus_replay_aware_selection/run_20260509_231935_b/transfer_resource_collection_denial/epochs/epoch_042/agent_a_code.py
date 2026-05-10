def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    resources_list = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    res = {(p[0], p[1]) for p in resources_list}
    obs = {(p[0], p[1]) for p in obstacles_list}

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources_list:
        return [0, 0]

    # Immediate pickup if possible
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res and (nx, ny) not in obs:
            return [dx, dy]

    # Pick step that maximizes advantage on best available resource
    best_move = (0, 0)
    best_val = -10**18

    # Precompute opponent distances to each resource once
    opp_to = {}
    for rx, ry in res:
        if (rx, ry) not in obs:
            opp_to[(rx, ry)] = dist8(ox, oy, rx, ry)

    # If all resource cells are blocked, just avoid obstacles
    if not opp_to:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # One-ply evaluation: best resource we can claim after this move
        local_best = -10**18
        for (rx, ry), od in opp_to.items():
            sd = dist8(nx, ny, rx, ry)
            # Priority: resources we can reach sooner than opponent, then faster, then slight tie-break
            val = (od - sd) * 1000 - sd - (abs(rx - ox) + abs(ry - oy)) * 0.001 - (rx + 3 * ry) * 0.0001
            if val > local_best:
                local_best = val

        # Slightly prefer reducing own distance to opponent to block, but only if close
        opp_close = dist8(nx, ny, ox, oy)
        block_bonus = 0
        if opp_close <= 2:
            block_bonus = 5 * (2 - opp_close)

        local_best += block_bonus

        if local_best > best_val:
            best_val = local_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]