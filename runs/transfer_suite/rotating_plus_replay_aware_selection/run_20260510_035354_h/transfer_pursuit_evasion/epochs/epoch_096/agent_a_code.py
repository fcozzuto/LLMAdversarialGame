def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "")
    opp_role = str(observation.get("opponent_role") or "")
    s = (self_role + " " + opp_role).lower()

    pursue = ("pursuer" in self_role.lower()) or ("pursuer" in s and "evader" not in self_role.lower())

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # deterministic: avoid illegal/blocked by mapping to stay
        d = abs(nx - ox) + abs(ny - oy)
        v = -d if pursue else d
        # Slight obstacle-aware tie-break: prefer moves that increase free space when evading, minimize when pursuing
        free = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty) and (tx, ty) not in obstacles:
                free += 1
        if pursue:
            v = (v, free)  # maximize -d then free
        else:
            v = (v, -free)  # maximize d then minimize closeness to walls
        if best is None or v > bestv:
            bestv = v
            best = [dx, dy]

    return [int(best[0]), int(best[1])]