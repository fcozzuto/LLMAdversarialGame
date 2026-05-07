def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    res_set = set(resources)

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = sx + dx; ny = sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((dx, dy))
    if not cand:
        return [0, 0]

    best_move = cand[0]
    best_score = -10**18
    my_pos = (sx, sy)
    opp_pos = (ox, oy)

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        new_pos = (nx, ny)
        move_score = 0
        if (nx, ny) in res_set:
            move_score += 1000000
        # pick target resource to maximize "win-now" over opponent
        local_best = -10**18
        for rx, ry in resources:
            rpos = (rx, ry)
            myd = dist(new_pos, rpos)
            opd = dist(opp_pos, rpos)
            # self wants resources where it can arrive first (considering opponent's current position)
            win_margin = (opd - myd)
            # prefer closer with higher margin; encourage immediate steals
            val = (win_margin * 2000) - myd * 50
            if rpos == new_pos:
                val += 500000
            # slight bias to the center line to break ties deterministically
            val -= abs((rx - (w - 1) / 2)) + abs((ry - (h - 1) / 2)) * 0.01
            if val > local_best:
                local_best = val
        # also reward reducing distance to the most contested resource
        move_score += local_best
        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]