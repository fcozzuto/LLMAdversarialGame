def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Interceptor/edge-contest: head for frontier unclaimed cells adjacent to opponent territory.
    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                yield x + dx, y + dy

    frontier = []
    for (x, y) in opp_t:
        for nx, ny in neighbors8(x, y):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked and (nx, ny) in unclaimed:
                frontier.append((nx, ny))
    frontier = list(dict.fromkeys(frontier))

    if not frontier:
        frontier = [(ox, oy)]
        if (ox, oy) in blocked or not (0 <= ox < w and 0 <= oy < h):
            frontier = [min(unclaimed, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy), default=(sx, sy))]
            if frontier and frontier[0] == (sx, sy) and not unclaimed:
                frontier = [(sx, sy)]

    # Choose best frontier cell deterministically.
    tx, ty = min(frontier, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), abs(c[0] - (w - 1) / 2) + abs(c[1] - (h - 1) / 2), c[0], c[1]))

    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny, dx, dy = sx, sy, 0, 0

        v = 0
        # Favor immediate flips/edge blocking.
        if (nx, ny) in opp_t:
            v += 1600
        if (nx, ny) in unclaimed:
            # Prioritize stepping onto frontier-adjacent unclaimed (edge contest).
            for ax, ay in neighbors8(nx, ny):
                if (ax, ay) in opp_t:
                    v += 900
                    break
            v += 40
        if (nx, ny) in self_t:
            v -= 25  # less focus on expanding; focus on contesting edges.

        # Move closer to target frontier.
        d = abs(nx - tx) + abs(ny - ty)
        v += 300 - 25 * d

        # Avoid drifting into opponent center if we can't contest.
        center_d = abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)
        v += 2 * center_d

        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = v
            best = [dx, dy]

    return best