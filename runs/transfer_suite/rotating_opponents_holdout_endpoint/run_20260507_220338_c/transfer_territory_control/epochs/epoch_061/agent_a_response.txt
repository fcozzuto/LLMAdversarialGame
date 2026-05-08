def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))
    def to_set(lst):
        s = set()
        for p in lst or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s
    self_terr = to_set(observation.get("self_territory") or [])
    opp_terr = to_set(observation.get("opponent_territory") or [])
    unclaimed = to_set(observation.get("unclaimed_cells") or [])
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def adj8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx != 0 or dy != 0:
                    nx, ny = x + dx, y + dy
                    if inb(nx, ny):
                        yield nx, ny
    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_pos = observation.get("opponent_position") or (w - 1, h - 1)
    opp_pos = (int(opp_pos[0]), int(opp_pos[1]))

    frontier = []
    for c in unclaimed:
        if any(n in opp_terr for n in adj8(c[0], c[1])):
            frontier.append(c)
    if frontier:
        target = min(frontier, key=lambda c: (man((sx, sy), c), c[0], c[1]))
    else:
        candidates = list(unclaimed)
        if candidates:
            target = min(candidates, key=lambda c: (man((sx, sy), c), c[0], c[1]))
        else:
            target = opp_pos  # fallback

    best_move = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = 0.0
        if (nx, ny) in opp_terr:
            v += 20.0
        if (nx, ny) in self_terr:
            v += 1.5
        if (nx, ny) in unclaimed:
            v += 6.0
            if any(n in opp_terr for n in adj8(nx, ny)):
                v += 14.0
            if any(n in self_terr for n in adj8(nx, ny)):
                v += 3.0
        dtarget = man((nx, ny), target)
        v += (-0.9 * dtarget)
        v += (-0.15 * man((nx, ny), opp_pos))
        if v > bestv:
            bestv = v
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]