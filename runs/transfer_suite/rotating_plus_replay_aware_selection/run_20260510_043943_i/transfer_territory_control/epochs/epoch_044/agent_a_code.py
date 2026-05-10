def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set()
    for p in observation.get("self_territory", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                self_terr.add((x, y))

    opp_terr = set()
    for p in observation.get("opponent_territory", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_terr.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.add((x, y))

    # Frontier targets: unclaimed cells adjacent to opponent territory (steal edge)
    frontier = set()
    for (ox, oy) in opp_terr:
        for dx, dy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)):
            nx, ny = ox + dx, oy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unclaimed:
                frontier.add((nx, ny))

    # If no frontier, go to nearest unclaimed
    targets = list(frontier) if frontier else list(unclaimed)
    if not targets:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (None, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        score = 0

        if cell in opp_terr:
            score += 60
        elif cell in unclaimed:
            score += 35
        elif cell in self_terr:
            score += 10

        # Distance to best target (lower is better)
        dist = 10**9
        for tx, ty in targets:
            d = abs(tx - nx) + abs(ty - ny)
            if d < dist:
                dist = d
        score += -dist

        # Nudge to keep pushing on the opponent side (not center-ish)
        if observation.get("turn_index", 0) % 2 == 0:
            ox_sum = 0
            oy_sum = 0
            # approximate opponent corner bias from current opponent position
            # (deterministic but cheap)
            op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
            ox, oy = int(op[0]), int(op[1])
            ox_sum, oy_sum = ox, oy
            score += -(abs(ox_sum - nx) + abs(oy_sum - ny)) // 3

        if best[0] is None or score > best[1]:
            best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]