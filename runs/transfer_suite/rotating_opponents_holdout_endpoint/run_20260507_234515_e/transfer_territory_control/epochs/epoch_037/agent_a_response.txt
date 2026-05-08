def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    oppT = to_set("opponent_territory")
    selfT = to_set("self_territory")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Prefer capturing nearby unclaimed/opponent cells; keep moves safe around obstacles.
    best = (0, 0)
    best_val = -10**18

    # Heuristic target type: if resources exist, prioritize them; else edge unclaimed; else opp territory.
    res_list = list(resources)
    if res_list:
        mode = "resource"
        target = min(res_list, key=lambda p: dist(sx, sy, p[0], p[1]))
    else:
        edge_unclaimed = [p for p in unclaimed if p[0] in (0, w - 1) or p[1] in (0, h - 1)]
        if edge_unclaimed:
            mode = "edge"
            target = min(edge_unclaimed, key=lambda p: dist(sx, sy, p[0], p[1]))
        elif unclaimed:
            mode = "unclaimed"
            target = min(unclaimed, key=lambda p: dist(sx, sy, p[0], p[1]))
        elif oppT:
            mode = "attack"
            target = min(list(oppT), key=lambda p: dist(sx, sy, p[0], p[1]))
        else:
            mode = "hold"
            target = (sx, sy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        # Immediate capture gains
        if (nx, ny) in resources:
            val += 400
        if (nx, ny) in unclaimed:
            val += 120
        if (nx, ny) in oppT:
            val += 90

        # Stay within/near frontier: avoid walking deeper into your territory unless progressing.
        if (nx, ny) in selfT:
            # discourage pointless moves
            val -= 8

        # Approach the chosen target
        d = dist(nx, ny, target[0], target[1])
        val += 60 - 10 * d

        # Block/synergize vs opponent: move to reduce their distance to our frontier and to target.
        od = dist(nx, ny, ox, oy)
        val -= 0.8 * od

        # If mode is attack, prefer moves that also get closer to a "contact line" with opponent.
        if mode == "attack":
            val += 0.5 * (dist(sx, sy, target[0], target[1]) - d)

        # Minor preference for staying if currently boxed
        if dx == 0 and dy == 0:
            val -= 2

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]