def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in blocked

    un_set = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                un_set.add((x, y))

    opp_set = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                opp_set.add((x, y))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = (1e18, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        score = 0
        if un_set:
            score = min(abs(nx - tx) + abs(ny - ty) for (tx, ty) in un_set)
        else:
            score = abs(nx - (W - 1) / 2) + abs(ny - (H - 1) / 2)
        if opp_set and (nx, ny) in opp_set:
            score -= 1e6
        if opp_set:
            near_opp = 0
            for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if (nx + adx, ny + ady) in opp_set:
                    near_opp += 1
            score -= 100 * near_opp
        score += 0.3 * (abs(nx - ox) + abs(ny - oy))
        if score < best[0] or (score == best[0] and (dx, dy) == best[1]):
            best = (score, [dx, dy])

    if best[1] is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best[1]