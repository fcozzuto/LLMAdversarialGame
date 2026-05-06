def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Resource-denial / steal: target what the opponent is closest to.
    best = None
    for rx, ry in resources:
        od = man(ox, oy, rx, ry)
        sd = man(sx, sy, rx, ry)
        val = (-od, sd, rx, ry)  # minimize od, then sd
        if best is None or val < best[0]:
            best = (val, rx, ry)
    _, tx, ty = best
    opd = man(ox, oy, tx, ty)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                ourd = man(nx, ny, tx, ty)
                # Prefer moves that improve race advantage toward opponent's target.
                score = (opd - ourd) * 1000 - ourd
                # Deterministic tie-break: favor diagonals, then toward increasing x, then increasing y.
                diag = 1 if (dx != 0 and dy != 0) else 0
                tie = (-diag, -dx, -dy)
                moves.append((score, tie, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(reverse=True)
    _, _, dx, dy = moves[0]
    return [int(dx), int(dy)]