def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obst = set((x, y) for x, y in obstacles)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def clamp(x, a, b): return a if x < a else (b if x > b else x)
    def dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Target selection: pick resource that gives the largest distance advantage over opponent
    if resources:
        best = None
        best_score = -10**18
        for rx, ry in resources:
            sdist = abs(rx - sx) + abs(ry - sy)
            odist = abs(rx - ox) + abs(ry - oy)
            score = odist - sdist
            if score > best_score or (score == best_score and (sdist < best[0])):
                best_score = score
                best = (sdist, rx, ry)
        _, tx, ty = best
    else:
        # If no resources known, drift toward center while keeping away from obstacles
        tx, ty = w // 2, h // 2

    # Movement selection: greedy step toward target with deterministic tie-breaks
    best_move = (0, 0)
    best_val = 10**18
    best_adv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        nx = clamp(nx, 0, w - 1)
        ny = clamp(ny, 0, h - 1)
        if (nx, ny) in obst:
            continue
        d = abs(tx - nx) + abs(ty - ny)
        # Advantage: how much farther target is from opponent than from us after move
        adv = (abs(tx - ox) + abs(ty - oy)) - d
        if d < best_val or (d == best_val and adv > best_adv):
            best_val = d
            best_adv = adv
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]