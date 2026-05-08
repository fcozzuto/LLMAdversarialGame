def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = [(int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or [])]

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    oppd = lambda x, y: man(x, y, ox, oy)
    mind_to = None
    if unclaimed:
        def mind_un(x, y):
            return min(man(x, y, ux, uy) for ux, uy in unclaimed)
    else:
        def mind_un(x, y):
            return 3

    resmind = None
    if resources:
        def mind_res(x, y):
            return min(man(x, y, rx, ry) for rx, ry in resources)
    else:
        def mind_res(x, y):
            return 4

    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        sc = 0.0

        if (nx, ny) in opp_terr:
            sc += 6.0  # flipping on entry
        if (nx, ny) in self_terr:
            sc += 0.8  # maintain control
        if (nx, ny) not in self_terr and (nx, ny) not in opp_terr:
            sc += 1.0  # likely unclaimed, good to expand

        # push to unclaimed, but keep away from opponent to avoid being swept
        sc += -0.45 * mind_un(nx, ny)
        sc += -0.10 * oppd(nx, ny)

        # opportunistic resource pressure
        sc += -0.30 * mind_res(nx, ny)

        # small tie-break toward edges early to secure frontier (deterministic)
        if (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1):
            sc += 0.15

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)
        elif sc == best_sc and best is not None:
            # deterministic tie-break: prefer staying still, then lexicographic
            if (dx, dy) == (0, 0) and best != (0, 0):
                best = (dx, dy)
            elif (dx, dy) != best and (dx, dy) < best:
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]