def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    self_t = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = None
    bestv = -10**18

    if opp_t:
        opp_list = sorted(opp_t)
        opp_target = min(opp_list, key=lambda t: (dist((sx, sy), t), t[0], t[1]))
    else:
        opp_target = None

    if unclaimed:
        uncl_list = sorted(unclaimed)
        uncl_target = min(uncl_list, key=lambda t: (dist((sx, sy), t), t[0], t[1]))
    else:
        uncl_target = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = 0
        cur = (nx, ny)

        if cur in opp_t:
            v += 60
        elif cur in unclaimed:
            v += 8
        elif cur in self_t:
            v += 2

        if opp_target is not None:
            dcur = dist((nx, ny), opp_target)
            v += (30 - dcur)
        elif uncl_target is not None:
            dcur = dist((nx, ny), uncl_target)
            v += (18 - dcur)
        else:
            v += -(abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))

        # Edge pressure: prefer moves adjacent to opponent territory.
        if opp_t:
            adj = False
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    tx, ty = nx + ax, ny + ay
                    if (tx, ty) in opp_t:
                        adj = True
                        break
                if adj:
                    break
            if adj:
                v += 12

        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]