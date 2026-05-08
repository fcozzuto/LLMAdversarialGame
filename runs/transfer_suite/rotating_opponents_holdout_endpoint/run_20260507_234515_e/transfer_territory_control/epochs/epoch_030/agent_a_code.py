def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def parse_pos_list(key):
        out = []
        for p in observation.get(key) or []:
            if p is None or len(p) < 2:
                continue
            out.append((int(p[0]), int(p[1])))
        return out

    obstacles = set(parse_pos_list("obstacles"))
    resources = parse_pos_list("resources")
    unclaimed = parse_pos_list("unclaimed_cells")

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def free(x, y):
        return inside(x, y) and (x, y) not in obstacles

    targets = resources if resources else unclaimed
    if targets:
        best = None
        best_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            # minimize distance to nearest target; add small tie-break by closeness advantage vs opponent
            md_self = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
            md_opp = min(abs(ox - tx) + abs(oy - ty) for tx, ty in targets)
            score = (md_self, md_self - md_opp, -nx, -ny)
            if best is None or score < best_score:
                best, best_score = (dx, dy), score
        if best is not None:
            return [best[0], best[1]]

    # No targets or no legal moves toward them: step away from opponent if possible, else toward center
    legal = [(dx, dy) for dx, dy in dirs if free(sx + dx, sy + dy)]
    if not legal:
        # If stuck completely, move to any non-obstacle in-bounds via 8-neighborhood (deterministic)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if free(nx, ny):
                    return [dx, dy]
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        dist_away = abs(nx - ox) + abs(ny - oy)
        dist_center = abs(nx - cx) + abs(ny - cy)
        score = (-dist_away, dist_center, nx, ny)
        if best is None or score < best_score:
            best, best_score = (dx, dy), score
    return [best[0], best[1]]