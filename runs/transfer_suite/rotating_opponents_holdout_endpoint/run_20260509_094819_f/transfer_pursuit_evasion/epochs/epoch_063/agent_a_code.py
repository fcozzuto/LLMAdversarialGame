def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    sr = (observation.get("self_role") or "").lower()
    pursuer = "pursuer" in sr

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = None

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        v = -d if pursuer else d
        if bestv is None or v > bestv:
            bestv = v
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best