def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < int(w) and 0 <= y < int(h):
                obstacles.add((x, y))

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < int(w) and 0 <= y < int(h) and (x, y) not in obstacles:
                resources.append((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < int(w) and 0 <= y < int(h) and (x, y) not in obstacles:
                unclaimed.append((x, y))

    def ok(x, y):
        return 0 <= x < int(w) and 0 <= y < int(h) and (x, y) not in obstacles

    cx, cy = (int(w) - 1) / 2.0, (int(h) - 1) / 2.0

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    best_sc = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sc = 0
        if (nx, ny) in resources:
            sc += 10000
        if (nx, ny) in unclaimed:
            sc += 2000
        if (nx, ny) in self_terr:
            sc += 200
        if (nx, ny) in opp_terr:
            sc -= 800

        dist_opp = abs(nx - ox) + abs(ny - oy)
        sc -= dist_opp * 20

        if resources:
            dmin = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
            sc += max(0, 800 - dmin * 30)
        else:
            sc += -((nx - cx) ** 2 + (ny - cy) ** 2) * 0.5

        if sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]