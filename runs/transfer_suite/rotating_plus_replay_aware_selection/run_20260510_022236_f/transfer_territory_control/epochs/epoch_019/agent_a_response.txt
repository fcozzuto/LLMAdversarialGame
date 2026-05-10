def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    dirs = [(0, -1), (0, 1), (-1, 0), (1, 0), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    unclaimed = observation.get("unclaimed_cells") or []
    opp_terr = observation.get("opponent_territory") or []
    if not unclaimed and not opp_terr:
        return [0, 0]

    # Alternate focus deterministically: expand unclaimed, then counter-claim near opponent.
    t = int(observation.get("turn_index", 0) or 0)
    focus_counter = (t % 4 == 1) or (t % 4 == 3)

    if focus_counter and opp_terr:
        # Target an opponent-occupied cell that is close, with slight bias toward our direction of travel.
        best = None
        bestv = 10**9
        for x, y in opp_terr:
            if (x, y) in blocked or not (0 <= x < w and 0 <= y < h):
                continue
            d = abs(x - sx) + abs(y - sy)
            bias = abs((x - ox)) + abs((y - oy))  # prefer cells closer to mid/interaction zone
            v = d * 10 + bias
            if v < bestv:
                bestv = v
                best = (x, y)
        target = best if best is not None else (ox, oy)
    else:
        # Prefer unclaimed closest to us, but biased to move toward opponent and center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        bestv = 10**18
        for x, y in unclaimed:
            if (x, y) in blocked or not (0 <= x < w and 0 <= y < h):
                continue
            d = abs(x - sx) + abs(y - sy)
            toward_opp = abs((x - ox)) + abs((y - oy))
            toward_center = abs(x - cx) + abs(y - cy)
            v = d * 5 + toward_opp * 2 + toward_center * 0.5
            if v < bestv:
                bestv = v
                best = (x, y)
        target = best if best is not None else (ox, oy)

    tx, ty = int(target[0]), int(target[1])

    best_move = (0, 0)
    bestv = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        # Greedy toward target; add small penalty for stopping unless needed.
        v = abs(tx - nx) + abs(ty - ny)
        if dx == 0 and dy == 0:
            v += 1.0
        # If we can flip, being nearer to opponent territory is better.
        # Use proximity to opponent position as proxy.
        v += 0.15 * (abs(nx - ox) + abs(ny - oy))
        if v < bestv:
            bestv = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]