def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    blocked = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    frontier = set()
    for x, y in opp_t:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in opp_t and (nx, ny) not in blocked:
                if (nx, ny) in unclaimed or (nx, ny) in self_t:
                    frontier.add((nx, ny))

    d_opp = abs(sx - ox) + abs(sy - oy)
    prefer_frontier = (d_opp > 8)

    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny, dx, dy = sx, sy, 0, 0

        v = 0
        if (nx, ny) in opp_t:
            v += 2000
        if (nx, ny) in frontier:
            v += 900
        if (nx, ny) in unclaimed:
            v += 320
        if (nx, ny) in self_t:
            v -= 10

        v += 260 - 18 * (abs(nx - ox) + abs(ny - oy))
        if prefer_frontier:
            v += (600 if (nx, ny) in frontier else 0)
        else:
            v += (200 if (nx, ny) in unclaimed else 0)

        # discourage stepping into regions adjacent to obstacles/edges for stability
        edge_pen = 0
        if nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1:
            edge_pen += 18
        for adx, ady in dirs:
            ax, ay = nx + adx, ny + ady
            if (ax, ay) in blocked:
                edge_pen += 6
        v -= edge_pen

        if v > bestv:
            bestv = v
            best = [dx, dy]

    return [int(best[0]), int(best[1])]