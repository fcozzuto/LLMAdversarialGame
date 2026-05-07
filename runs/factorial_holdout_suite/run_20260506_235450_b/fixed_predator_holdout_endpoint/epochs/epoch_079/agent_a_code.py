def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res_cells = []
    for r in resources:
        if len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                res_cells.append((x, y))
    if not res_cells:
        return [0, 0]

    best = (0, 0)
    best_key = (-10**9, 10**9, 10**9)

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        self_here = (nx, ny)
        best_for_move = (-10**9, 10**9, 10**9)
        for cell in res_cells:
            sd = man(self_here, cell)
            od = man((ox, oy), cell)
            adv = od - sd  # positive means we are closer (good)
            # If we can arrive no later than opponent, strongly prefer it.
            arrive_bonus = 40 if sd <= od else 0
            # Prefer resources that are nearer to us overall when tied.
            key = (adv + arrive_bonus, sd, abs((cell[0] - nx)) + abs((cell[1] - ny)))
            if key > best_for_move:
                best_for_move = key
        # Tie-break: prefer higher immediate advantage; then lower distance to chosen target.
        if best_for_move > best_key:
            best_key = best_for_move
            best = (dx, dy)

    return [int(best[0]), int(best[1])]