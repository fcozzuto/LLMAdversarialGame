def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    my_ter = set()
    for p in (observation.get("self_territory") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            my_ter.add((int(p[0]), int(p[1])))

    opp_ter = set()
    for p in (observation.get("opponent_territory") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_ter.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if unclaimed:
        tx, ty = unclaimed[0]
        bestd = abs(tx - sx) + abs(ty - sy)
        for x, y in unclaimed[1:]:
            d = abs(x - sx) + abs(y - sy)
            if d < bestd:
                bestd, tx, ty = d, x, y
    else:
        tx, ty = (w // 2), (h // 2)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        score = 0
        score -= 2 * (abs(nx - tx) + abs(ny - ty))
        if (nx, ny) in unclaimed:
            score += 50
        if (nx, ny) in my_ter:
            score += 5
        if (nx, ny) in opp_ter:
            score -= 40
        od = abs(nx - ox) + abs(ny - oy)
        score += 3 if od > 0 else 0
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if not legal(sx + dx, sy + dy):
        for d in dirs:
            nx, ny = sx + d[0], sy + d[1]
            if legal(nx, ny):
                return [int(d[0]), int(d[1])]
        return [0, 0]
    return [int(dx), int(dy)]