def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    def to_set(v):
        s = set()
        for p in (v or []):
            if not p or len(p) < 2:
                continue
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                s.add((x, y))
        return s

    obstacles = to_set(observation.get("obstacles"))
    resources = to_set(observation.get("resources"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    opp_t = to_set(observation.get("opponent_territory"))
    opp_pos = observation.get("opponent_position") or [sx, sy]
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def best_score(nx, ny):
        score = 0
        if (nx, ny) in resources:
            score += 10000
        if (nx, ny) in unclaimed:
            score += 2000
        if (nx, ny) in opp_t:
            score += 3000
        # prefer moving toward nearest target type
        if resources:
            score += -min(abs(nx - tx) + abs(ny - ty) for tx, ty in resources)
        elif unclaimed:
            score += -min(abs(nx - tx) + abs(ny - ty) for tx, ty in unclaimed)
        else:
            score += -abs(nx - ox) - abs(ny - oy)
        # discourage standing still unless it hits something valuable
        if (nx, ny) == (sx, sy):
            score -= 5
        # discourage revisiting last self step (if available)
        p = observation.get("self_path") or []
        if len(p) >= 2:
            lx, ly = int(p[-2][0]), int(p[-2][1])
            if (nx, ny) == (lx, ly):
                score -= 15
        return score

    best = None
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        s = best_score(nx, ny)
        if s > best_s:
            best_s, best = s, [dx, dy]
    return best if best is not None else [0, 0]