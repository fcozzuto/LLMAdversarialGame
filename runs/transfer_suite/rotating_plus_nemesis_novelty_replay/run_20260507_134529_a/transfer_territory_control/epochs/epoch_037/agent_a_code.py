def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    opp_list = list(opp_terr)
    if not opp_list:
        opp_list = [(ox, oy)]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # distance to opponent pressure
        dmin = 10**9
        for tx, ty in opp_list:
            d = abs(nx - tx) + abs(ny - ty)
            if d < dmin:
                dmin = d

        v = dmin  # prefer staying away from opponent territory
        if (nx, ny) in unclaimed:
            v += 6
        else:
            # expand into frontier by rewarding adjacency to unclaimed
            if unclaimed:
                for ax, ay in ((nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1), (nx-1, ny-1), (nx+1, ny+1), (nx-1, ny+1), (nx+1, ny-1)):
                    if (ax, ay) in unclaimed:
                        v += 2
                        break

        if (nx, ny) in opp_terr:
            v -= 8  # avoid risky flips into likely-controlled center
        if not self_terr:
            if (nx, ny) == (sx, sy):
                v -= 1
        else:
            # mild cohesion: don't run away too far from our own territory
            dself = 10**9
            for fx, fy in self_terr:
                dd = abs(nx - fx) + abs(ny - fy)
                if dd < dself:
                    dself = dd
            v -= min(5, dself) * 0.2

        # deterministic tie-break: earlier dirs in list
        if v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]