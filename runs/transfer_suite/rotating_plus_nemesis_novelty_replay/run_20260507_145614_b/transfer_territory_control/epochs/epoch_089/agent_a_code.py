def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    opp_s = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                opp_s.add((x, y))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    def adj_opp(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    if (nx, ny) in opp_s:
                        c += 1
        return c

    if not unclaimed and opp_s:
        # Fallback: try to enter opponent territory if no unclaimed remain
        targets = list(opp_s)
    else:
        targets = unclaimed

    if not targets:
        return [0, 0]

    # Pick best target deterministically
    best = None
    best_key = None
    for (tx, ty) in targets:
        d_edge = edge_dist(tx, ty)  # prefer interior
        a_opp = adj_opp(tx, ty)   # prefer contested flips
        md = (abs(tx - sx) + abs(ty - sy))
        key = (-a_opp, -d_edge, md, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best

    # Choose 1-step move that reduces distance and avoids obstacles; diagonal allowed.
    best_move = [0, 0]
    best_move_key = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            dist = abs(tx - nx) + abs(ty - ny)
            # Encourage approaching, but also slightly prefer adjacency to opponent to start flipping sooner
            a = 0
            for ddx in (-1, 0, 1):
                for ddy in (-1, 0, 1):
                    if ddx == 0 and ddy == 0:
                        continue
                    px, py = nx + ddx, ny + ddy
                    if 0 <= px < w and 0 <= py < h and (px, py) in opp_s:
                        a += 1
            key = (dist, -a, abs(dx) + abs(dy), nx, ny)
            if best_move_key is None or key < best_move_key:
                best_move_key = key
                best_move = [dx, dy]

    return best_move