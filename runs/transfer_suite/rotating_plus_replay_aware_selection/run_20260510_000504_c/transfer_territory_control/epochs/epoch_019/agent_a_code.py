def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    oxp, oyp = observation.get("opponent_position") or (sx, sy)
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    opp_list = list(opp_terr)
    def dist_to_opp_terr(x, y):
        if opp_list:
            md = 10**9
            for px, py in opp_list:
                d = manh(x, y, px, py)
                if d < md:
                    md = d
            return md
        return manh(x, y, oxp, oyp)

    cand_dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in cand_dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        d = dist_to_opp_terr(nx, ny)
        if (nx, ny) in opp_terr:
            base = 60.0
        elif (nx, ny) in unclaimed:
            base = 22.0
        elif (nx, ny) in self_terr:
            base = 4.0
        else:
            base = 1.0

        adj = 0
        for ax, ay in cand_dirs:
            px, py = nx + ax, ny + ay
            if inb(px, py) and (px, py) in opp_terr:
                adj += 1
            if inb(px, py) and (px, py) in unclaimed:
                adj += 0.4

        # Prefer closer to opponent-controlled/unclaimed while still taking captures.
        score = base + (10.0 / (1.0 + d)) + adj * 0.6
        key = (score, -d, -dx, -dy, nx, ny)
        if best is None or key > best[0]:
            best = (key, (dx, dy))

    if best is None:
        return [0, 0]
    return [best[1][0], best[1][1]]