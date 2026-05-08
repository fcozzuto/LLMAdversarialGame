def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    role = observation.get("self_role") or ""
    pursuer = ("purs" in role.lower()) or role.lower() == "pursuer" or role.lower() == "chaser"

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dsq = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Evader also avoids stepping into cells that reduce distance too much.
        # Tie-break deterministically by lexicographic move order already fixed by deltas.
        score = dsq if not pursuer else -dsq
        # Tiny bias to prefer not moving if equally good (via fixed score for center).
        if dx == 0 and dy == 0:
            score += -0.0001 if pursuer else 0.0001
        if best is None or score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]