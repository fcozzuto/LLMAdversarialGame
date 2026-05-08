def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))

    if not unclaimed:
        resources = toset(observation.get("resources"))
        if resources:
            unclaimed = set(resources)

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick move by local heuristic: secure far unclaimed / opportunistically flip nearby opponent territory.
    best = (float("-inf"), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        cell = (nx, ny)

        d_opp = man(nx, ny, ox, oy)
        d_self = man(nx, ny, sx, sy)

        if cell in oppT:
            base = 18
        elif cell in unclaimed:
            base = 22
        elif cell in selfT:
            base = 6
        else:
            base = 2

        # Further from opponent is safer for claimed frontier; also prefer reducing distance to unclaimed.
        # Compute nearest-unclaimed distance cheaply from a few candidates (deterministic subset).
        nearest_un = 999
        if unclaimed:
            cnt = 0
            for ux, uy in unclaimed:
                dist = man(nx, ny, ux, uy)
                if dist < nearest_un:
                    nearest_un = dist
                cnt += 1
                if cnt >= 20 and nearest_un == 0:
                    break

        # Deterrence: if opponent is very close, prioritize stepping into unclaimed/opp territory.
        urgency = 12 if d_opp <= 2 else 0
        score = base + (d_opp * 1.1) + (0 if nearest_un == 999 else (10 - min(10, nearest_un)) * 1.0) + urgency - d_self * 0.01

        # Deterministic tie-break: fixed ordering by dx,dy in moves list.
        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]