def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    self_t = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                self_t.add((x, y))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                opp_t.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                unclaimed.append((x, y))
    unclaimed_set = set(unclaimed)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Target: if opponent is close, counterclaim; else expand to nearest unclaimed
    if unclaimed:
        # nearest unclaimed, but prefer those closer to opponent (to cut them off)
        target = min(unclaimed, key=lambda c: (abs(c[0]-sx)+abs(c[1]-sy)) - 0.05*(abs(c[0]-ox)+abs(c[1]-oy)))
    else:
        target = None

    opp_near = []
    for p in opp_t:
        d = abs(p[0]-sx) + abs(p[1]-sy)
        if d <= 4:
            opp_near.append((d, p))
    opp_near.sort()

    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        v = 0
        cell = (nx, ny)
        if cell in opp_t:
            v += 120  # immediate counterclaim is very valuable (flip on entry)
        elif cell in unclaimed_set:
            v += 35
        elif cell in self_t:
            v += 8  # keep territory stable

        # Strategic pressure: move toward target unless it would drift away while opponent is countering
        if target is not None:
            v += -1.2 * (abs(nx-target[0]) + abs(ny-target[1]))
        else:
            v += -0.9 * (abs(nx-ox) + abs(ny-oy))

        # If opponent is near, prefer stepping closer to their territory boundary
        if opp_near:
            _, (tx, ty) = opp_near[0]
            v += -2.0 * (abs(nx-tx) + abs(ny-ty))

        # Slightly prefer moves that reduce distance to opponent (helps counterclaim archetype)
        v += -0.15 * (abs(nx-ox) + abs(ny-oy))

        # Deterministic tie-breaker: smallest (dx,dy) in order we iterate; if equal, keep first
        if v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]