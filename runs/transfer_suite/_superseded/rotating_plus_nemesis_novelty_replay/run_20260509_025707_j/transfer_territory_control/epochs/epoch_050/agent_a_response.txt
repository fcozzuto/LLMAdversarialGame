def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    self_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}
    myc = observation.get("self_territory_count", len(self_set))
    opc = observation.get("opponent_territory_count", len(opp_set))

    cx = cy = 0
    if opp_set:
        for x, y in opp_set:
            cx += x
            cy += y
        cx /= float(len(opp_set))
        cy /= float(len(opp_set))
    else:
        cx, cy = w - 1 - sx, h - 1 - sy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_adj = set()
    for x, y in opp_set:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inside(nx, ny):
                    opp_adj.add((nx, ny))

    un_list = list(unclaimed)[:64]  # cap for speed/determinism
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort()

    best = None
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        cell = (nx, ny)

        score = 0
        dcen_before = dist((sx, sy), (cx, cy))
        dcen_after = dist((nx, ny), (cx, cy))
        score += (dcen_before - dcen_after) * 2.0  # move away from opponent pressure

        if cell in self_set:
            score += 0.3
        elif cell in opp_set:
            score += 6.0 if myc < opc else -1.5  # flip only if we're behind
        elif cell in unclaimed:
            score += 3.0  # prefer claiming unclaimed

        if cell in opp_adj:
            score += 5.0 if myc < opc else -2.0  # if behind, attack frontier

        if un_list:
            du = 10**9
            for p in un_list:
                d = abs(p[0] - nx) + abs(p[1] - ny)
                if d < du:
                    du = d
            score += max(0.0, 3.0 - du)  # closer to some unclaimed

        # slight tie-break toward reducing distance to center of grid
        gx, gy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= 0.01 * dist((nx, ny), (gx, gy))

        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]