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

    cx, cy = (sx + ox) // 2, (sy + oy) // 2
    dirx = 1 if ox > sx else (-1 if ox < sx else 0)
    diry = 1 if oy > sy else (-1 if oy < sy else 0)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny = sx, sy
            dx, dy = 0, 0

        v = 0
        if (nx, ny) in opp_t:
            v += 1200
        elif (nx, ny) in unclaimed:
            v += 420
        elif (nx, ny) in self_t:
            v += 40

        d_opp = abs(nx - ox) + abs(ny - oy)
        v += 260 - 22 * d_opp  # intercept: get closer to opponent

        # tighten around the frontier (midpoint + direction from us to them)
        fx, fy = cx + dirx, cy + diry
        d_front = abs(nx - fx) + abs(ny - fy)
        v += 140 - 10 * d_front

        # avoid drifting away from opponent if we didn't gain territory
        if (nx, ny) not in opp_t and (nx, ny) not in unclaimed:
            v -= 30 * (d_opp - (abs(sx - ox) + abs(sy - oy)) + 1)

        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best