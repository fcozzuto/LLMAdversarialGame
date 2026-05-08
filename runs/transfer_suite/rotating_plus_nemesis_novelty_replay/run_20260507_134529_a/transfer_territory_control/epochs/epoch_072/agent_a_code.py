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
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    opp_cells = opp_terr if opp_terr else {(ox, oy)}
    cx = sum(x for x, _ in opp_cells) / len(opp_cells)
    cy = sum(y for _, y in opp_cells) / len(opp_cells)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def frontier_value(x, y):
        if (x, y) in opp_terr:
            return 9.0
        if (x, y) in unclaimed:
            return 4.0
        if (x, y) in self_terr:
            return 1.0
        return 0.8

    def dist_to_centroid(x, y):
        dx = x - cx
        dy = y - cy
        return (dx * dx + dy * dy) ** 0.5

    best = [0, 0]
    best_score = -1e18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        sc = frontier_value(nx, ny)
        if (nx, ny) in resources:
            sc += 2.5
        # Aggressive: head into opponent center; extra incentive for unclaimed/opp.
        sc += 2.0 / (1.0 + dist_to_centroid(nx, ny))
        # Keep from wandering: slight penalty if not improving closeness.
        cur = dist_to_centroid(sx, sy)
        nxt = dist_to_centroid(nx, ny)
        sc += 0.6 if nxt < cur else -0.2
        if sc > best_score or (sc == best_score and (dx, dy) < tuple(best)):
            best_score = sc
            best = [dx, dy]
    return best