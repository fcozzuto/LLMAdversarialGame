def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_score = -10**18
    if not resources:
        # chase opponent slightly if no resources
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                score = -md((nx, ny), (ox, oy))
                if score > best_score:
                    best_score = score
                    best = [dx, dy]
        return [int(best[0]), int(best[1])]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        my_pos = (nx, ny)

        my_best = 10**9
        opp_best = 10**9
        for rx, ry in resources:
            d = abs(rx - nx) + abs(ry - ny)
            if d < my_best:
                my_best = d
        # approximate opponent threat: how close opponent is to resources
        for rx, ry in resources:
            d = abs(rx - ox) + abs(ry - oy)
            if d < opp_best:
                opp_best = d

        # Prefer moves that get closer to a resource and increase distance from opponent-best
        score = -my_best + (my_best - opp_best) * 0.2 - (abs(dx) + abs(dy)) * 0.01
        if score > best_score:
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]