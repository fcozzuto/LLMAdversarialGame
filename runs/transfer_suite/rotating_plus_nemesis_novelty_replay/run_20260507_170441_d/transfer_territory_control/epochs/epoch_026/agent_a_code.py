def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            blocked.add((x, y))

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    opp_cnt = int(observation.get("opponent_territory_count", len(opp_t)) or 0)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    bestv = -10**18

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    neigh8 = dirs

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        v = 0
        if (nx, ny) in unclaimed:
            v += 900
        if (nx, ny) in self_t:
            v += 30
        if (nx, ny) in opp_t:
            if opp_cnt <= max(1, len(opp_t)):
                v -= 80
            else:
                v -= 120
            v += 350  # flipping payoff, but still generally risky

        # frontier quality: how good the local area looks from this move
        u = s = o = 0
        for ex, ey in neigh8:
            ax, ay = nx + ex, ny + ey
            if not (0 <= ax < w and 0 <= ay < h) or (ax, ay) in blocked:
                continue
            if (ax, ay) in unclaimed:
                u += 1
            elif (ax, ay) in self_t:
                s += 1
            elif (ax, ay) in opp_t:
                o += 1
        v += 70 * u + 15 * s - 90 * o

        # avoid getting too close to opponent while they have momentum
        dO = abs(nx - ox) + abs(ny - oy)
        v += (320 - 18 * dO) if opp_cnt > 0 else (240 - 12 * dO)

        # slight bias toward expanding away from our center of mass (deterministic)
        if self_t:
            cx = sum(x for x, _ in self_t) / len(self_t)
            cy = sum(y for _, y in self_t) / len(self_t)
            v += 0.5 * (abs(nx - cx) + abs(ny - cy))

        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]