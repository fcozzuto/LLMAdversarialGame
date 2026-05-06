def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dxs = [-1, 0, 1]
    dys = [-1, 0, 1]
    moves = [(dx, dy) for dx in dxs for dy in dys]

    # Choose the resource where we can best beat the opponent (self closer than opponent).
    best_cell = None
    best_adv = None
    for rx, ry in resources:
        dS = dist((sx, sy), (rx, ry))
        dO = dist((ox, oy), (rx, ry))
        adv = (dO - dS)  # higher is better
        # Deterministic tie-break
        if best_cell is None or adv > best_adv or (adv == best_adv and (rx, ry) < best_cell):
            best_cell = (rx, ry)
            best_adv = adv

    rx, ry = best_cell

    # Evaluate immediate moves by advantage after the step toward the chosen cell.
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dS2 = dist((nx, ny), (rx, ry))
        dO2 = dist((ox, oy), (rx, ry))
        # Primary: maximize advantage at this resource; secondary: reduce our distance.
        sc = (dO2 - dS2, -dS2, -abs((nx - sx) - (ny - sy)))
        if best_move is None or sc > best_score or (sc == best_score and (dx, dy) < best_move):
            best_score = sc
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]