def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    def norm(p):
        try:
            return int(p[0]), int(p[1])
        except:
            return 0, 0

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = norm(p)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = norm(p)
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    resources = set()
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = norm(p)
            if 0 <= x < w and 0 <= y < h:
                resources.add((x, y))

    self_ter = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = norm(p)
            if 0 <= x < w and 0 <= y < h:
                self_ter.add((x, y))

    opp_ter = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = norm(p)
            if 0 <= x < w and 0 <= y < h:
                opp_ter.add((x, y))

    opp_pos = observation.get("opponent_position") or [sx, sy]
    ox, oy = norm(opp_pos)

    self_recent = set()
    path = observation.get("self_path") or []
    for p in path[-6:]:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = norm(p)
            if 0 <= x < w and 0 <= y < h:
                self_recent.add((x, y))

    opp_recent = set()
    opath = observation.get("opponent_path") or []
    for p in opath[-6:]:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = norm(p)
            if 0 <= x < w and 0 <= y < h:
                opp_recent.add((x, y))

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = (-10**9, (0, 0))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        val = 0
        if (nx, ny) in unclaimed:
            val += 10
        if (nx, ny) in resources:
            val += 6
        if (nx, ny) in self_ter:
            val += 3
        if (nx, ny) in opp_ter:
            val -= 3
        if (nx, ny) in self_recent:
            val -= 2
        if (nx, ny) in opp_recent:
            val -= 1
        val -= abs(nx - ox) * 0.1
        if val > best[0]:
            best = (val, (dx, dy))
    return [best[1][0], best[1][1]]