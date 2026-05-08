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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny, dx, dy = sx, sy, 0, 0
        moves.append((dx, dy, nx, ny))

    def adj_to_opp(x, y):
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in opp_t:
                    return True
        return False

    self_count = int(observation.get("self_territory_count", len(self_t)) or 0)
    opp_count = int(observation.get("opponent_territory_count", len(opp_t)) or 0)
    behind = self_count < opp_count

    best = None
    bestv = -10**18

    for dx, dy, nx, ny in moves:
        if (nx, ny) == (sx, sy):
            move_pen = 5
        else:
            move_pen = 0

        v = 0
        if (nx, ny) in opp_t:
            v += 1600  # immediate flip target
        elif (nx, ny) in unclaimed:
            v += 520
        elif (nx, ny) in self_t:
            v += 20
        else:
            v -= 30

        if adj_to_opp(nx, ny):
            v += 650 if behind else 320  # edge disruption priority

        # Avoid walking into opponent-adjacent traps if we're ahead
        if (nx, ny) not in self_t and (nx, ny) not in opp_t and adj_to_opp(nx, ny) and not behind:
            v -= 120

        # Distance bias: if behind, go towards opponent; else, go away from opponent
        d = abs(nx - ox) + abs(ny - oy)
        v += (-8 * d if behind else 4 * d)

        # Slight center preference to keep options open
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dc = abs(nx - cx) + abs(ny - cy)
        v += (-1.5 * dc)

        v -= move_pen

        if v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]