def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (W - 1, H - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    self_t = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            self_t.add((int(p[0]), int(p[1])))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            opp_t.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H

    def neigh_count(tset, x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in tset:
                    c += 1
        return c

    best = None
    best_val = -10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            if (nx, ny) == (sx, sy):
                continue

            v = 0
            if (nx, ny) in opp_t:
                v += 6
                v += neigh_count(opp_t, nx, ny) * 0.5
            elif (nx, ny) in unclaimed:
                v += 3
                v += min(neigh_count(opp_t, nx, ny), 8) * 0.35
            else:
                v += 0.2
                v += neigh_count(opp_t, nx, ny) * 0.15

            dc = abs(nx - cx) + abs(ny - cy)
            v += -0.05 * dc  # bias toward center to avoid edge-defense trapping

            dop = abs(nx - ox) + abs(ny - oy)
            v += -0.04 * max(dop - 1, 0)  # don't drift too far from contest

            # obstacle proximity penalty
            obp = 0
            for ex in (-1, 0, 1):
                for ey in (-1, 0, 1):
                    if ex == 0 and ey == 0:
                        continue
                    ax, ay = nx + ex, ny + ey
                    if inside(ax, ay) and (ax, ay) in obstacles:
                        obp += 1
            v += -0.3 * obp

            # deter stepping back onto own territory unless it advances toward center/contested
            if (nx, ny) in self_t:
                v += -0.2

            if v > best_val or (v == best_val and (dx, dy) < best):
                best_val = v
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]