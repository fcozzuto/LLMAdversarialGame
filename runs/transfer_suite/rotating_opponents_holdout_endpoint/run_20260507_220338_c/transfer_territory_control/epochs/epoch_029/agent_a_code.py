def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or (sx, sy)
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = p
        obstacles.add((int(x), int(y)))

    myset = set()
    for p in observation.get("self_territory") or []:
        x, y = p
        myset.add((int(x), int(y)))

    opset = set()
    for p in observation.get("opponent_territory") or []:
        x, y = p
        opset.add((int(x), int(y)))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        x, y = p
        unclaimed.add((int(x), int(y)))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    # Neighbor unclaimed adjacent to our territory (frontier)
    frontier = []
    for (x, y) in myset if myset else [(sx, sy)]:
        for dx, dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                frontier.append((nx, ny))
    if not frontier:
        frontier = list(unclaimed)

    if not frontier:
        return [0, 0]

    # Deterministic target choice: maximize (adjacency bonus - distance - opponent proximity)
    # Evaluate each candidate for its usefulness.
    best_target = None
    best_val = -10**18
    for tx, ty in frontier[:]:
        man = abs(tx - sx) + abs(ty - sy)
        oppd = abs(tx - ox) + abs(ty - oy)
        adj = 1 if any((tx + ddx, ty + ddy) in myset for ddx, ddy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))) else 0
        # Prefer expanding into unclaimed (big), reduce opponent approach (small), prefer reachable (small).
        val = (1000 * adj if adj else 300) - 3 * man + 0.5 * oppd
        if val > best_val:
            best_val = val
            best_target = (tx, ty)

    tx, ty = best_target

    # Choose best immediate move toward that target, avoiding obstacles; prefer unclaimed, then own territory, avoid opponent unless forced.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        base = - (abs(nx - tx) + abs(ny - ty))
        if cell in unclaimed:
            base += 800
        elif cell in myset:
            base += 40
        elif cell in opset:
            base -= 80
        # Nudge to reduce opponent distance when moving into risky areas
        base += 0.2 * (abs(nx - ox) + abs(ny - oy)) * (-1)
        if base > best_score or (base == best_score and (dx, dy) < best_move):
            best_score = base
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]