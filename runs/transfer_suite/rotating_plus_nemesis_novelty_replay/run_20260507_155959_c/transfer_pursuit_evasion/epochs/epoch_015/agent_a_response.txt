def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    sr = str(observation.get("self_role", "")).lower()
    i_am_evader = ("evader" in sr)
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist8(a, b):
        ax, ay = a
        bx, by = b
        if not inb(ax, ay) or not inb(bx, by):
            return 10**9
        if a == b:
            return 0
        q = [(ax, ay)]
        qi = 0
        seen = {a: 0}
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            d = seen[(x, y)] + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in seen:
                    if (nx, ny) == (bx, by):
                        return d
                    seen[(nx, ny)] = d
                    q.append((nx, ny))
        return 10**9

    if i_am_evader:
        best = (0, 0)
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = (abs(ox - nx) + abs(oy - ny))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Pursuer: predict evader's next move as the one maximizing distance from us,
    # then pick our move that minimizes distance to that predicted position.
    cand_ev = []
    for dx, dy in deltas:
        ex, ey = ox + dx, oy + dy
        if inb(ex, ey):
            cand_ev.append((ex, ey))
    if not cand_ev:
        cand_ev = [(ox, oy)]
    # Deterministic tie-break order for predicted position
    pred = None
    predv = -10**18
    for ex, ey in cand_ev:
        v = (abs(ex - sx) + abs(ey - sy))
        if v > predv:
            predv = v
            pred = (ex, ey)

    best = (0, 0)
    bestd = 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist8((nx, ny), pred)
        if d < bestd:
            bestd = d
            best = (dx, dy)
    return [best[0], best[1]]