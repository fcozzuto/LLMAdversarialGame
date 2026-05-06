def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        # Deterministic fallback: move toward center-ish while staying safe
        cx, cy = w // 2, h // 2
        best = (0, 0)
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = abs(nx - cx) + abs(ny - cy)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick target resource by maximizing our advantage over opponent
    best_r = resources[0]
    best_adv = None
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        adv = od - sd
        if best_adv is None or adv > best_adv or (adv == best_adv and sd < abs(best_r[0] - sx) + abs(best_r[1] - sy)):
            best_adv = adv
            best_r = (rx, ry)

    rx, ry = best_r
    cur_sd = abs(rx - sx) + abs(ry - sy)

    # Evaluate candidate moves by improvement in our distance-to-target and advantage vs opponent
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nsd = abs(rx - nx) + abs(ry - ny)
        nod = abs(rx - ox) + abs(ry - oy)
        # Score: primary reduce our distance; secondary increase (opponent_dist - our_dist) advantage; slight prefer safety
        primary = -(nsd)
        advantage = (nod - nsd)
        safety = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay) and (ax, ay) not in obstacles:
                safety += 1
        # Tie-break deterministically: prefer moves that reduce our distance more, then higher advantage, then lexicographic dx,dy
        score = (primary, advantage, safety, -abs(nx - sx) - abs(ny - sy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If no move improves, still choose the least bad move deterministically (already handled by scoring)
    return [best_move[0], best_move[1]]