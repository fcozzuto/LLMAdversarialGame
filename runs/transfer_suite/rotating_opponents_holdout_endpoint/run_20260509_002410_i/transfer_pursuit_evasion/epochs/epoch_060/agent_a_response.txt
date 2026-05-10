def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role) or ("catch" in role) or ("chase" in role) or ("seek" in role)
    if not ("evader" in role or "run" in role or "escape" in role) and "pursuer" not in role:
        pursuer = True  # default to chase

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    best = None
    best_score = None

    # Deterministic tie-breaking order: as listed in moves
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or blocked(nx, ny):
            continue
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # small preference for advancing toward/away with slight axis weighting
        axis = abs(nx - ox) + abs(ny - oy)
        if pursuer:
            # chase: minimize distance; break ties toward lower axis
            score = (-dist2, -axis, -((nx == ox) and (ny == oy)))
        else:
            # evade: maximize distance; break ties toward higher axis
            score = (dist2, axis, (nx == ox) and (ny == oy))
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    # If all candidate moves blocked/off-grid, stay still
    if best is None:
        return [0, 0]
    return best