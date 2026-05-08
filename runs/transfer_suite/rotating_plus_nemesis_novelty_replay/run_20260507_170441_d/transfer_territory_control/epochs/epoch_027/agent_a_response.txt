def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    adj_opp = abs(sx - ox) <= 1 and abs(sy - oy) <= 1
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny, dx, dy = sx, sy, 0, 0

        v = 0
        if (nx, ny) in opp_t:
            v += 900  # steal/flip
        if (nx, ny) in unclaimed:
            v += 520  # expand
        if (nx, ny) in self_t:
            v += 40

        d_goal = abs(nx - tx) + abs(ny - ty)
        v += 220 - 20 * d_goal

        d_opp = abs(nx - ox) + abs(ny - oy)
        if adj_opp:
            v += 60 if d_opp > 1 else -40  # avoid getting boxed in unless stealing
        v -= 6 * (abs(dx) + abs(dy))

        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best