def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        # Fallback: stay or move towards center to pressure
        target = (sx, sy)
    else:
        # deterministic heuristic: pick resource closest to me; break ties by farthest from opponent
        best_r = resources[0]
        best_d = abs(sx - best_r[0]) + abs(sy - best_r[1])
        best_od = abs(ox - best_r[0]) + abs(oy - best_r[1])
        for r in resources:
            d = abs(sx - r[0]) + abs(sy - r[1])
            od = abs(ox - r[0]) + abs(oy - r[1])
            if d < best_d or (d == best_d and od > best_od):
                best_r = r
                best_d = d
                best_od = od
        target = best_r

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Move towards target with simple priority: diagonals first for efficiency
    dx = dy = 0
    if target[0] > sx:
        dx = 1
    elif target[0] < sx:
        dx = -1
    if target[1] > sy:
        dy = 1
    elif target[1] < sy:
        dy = -1

    # If the chosen move is illegal, try alternative moves in a fixed deterministic order
    moves = [
        (dx, dy),
        (dx, 0),
        (0, dy),
        (dx * -1, dy),
        (dx, dy * -1),
        (-dx, dy),
        (-dx, 0) ,
        (0, -dy),
        (0, 0)
    ]

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if legal(nx, ny):
            return [mx, my]

    # If no legal move found (shouldn't happen), stay
    return [0, 0]