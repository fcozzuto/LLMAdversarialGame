def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    my = observation.get("self_territory") or []
    opp = observation.get("opponent_territory") or []
    un = observation.get("unclaimed_cells") or []

    my_set = set((int(p[0]), int(p[1])) for p in my if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_set = set((int(p[0]), int(p[1])) for p in opp if isinstance(p, (list, tuple)) and len(p) >= 2)
    un_list = [(int(p[0]), int(p[1])) for p in un if isinstance(p, (list, tuple)) and len(p) >= 2]
    un_set = set(un_list)

    # Prefer capturing unclaimed cells adjacent to our territory; otherwise grab nearest unclaimed;
    # if none, move toward nearest opponent territory.
    neigh8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    frontier = []
    for x, y in my_set:
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if (nx, ny) in un_set:
                frontier.append((nx, ny))
    if frontier:
        targets = frontier
    elif un_list:
        targets = un_list
    else:
        targets = list(opp_set)

    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)]

    # Deterministic tie-break: fixed ordering above; score drives choice.
    best = (0, 0)
    best_score = -10**18
    # Use few targets for speed; deterministic slice.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        score = 0
        if (nx, ny) in un_set:
            score += 50
        if (nx, ny) in opp_set:
            score += 35  # flipping opponent territory is beneficial
        # Chase best target by distance, with slight preference for edge-ish expansion (toward center-free control).
        if targets:
            dmin = 10**9
            edmin = 10**9
            for tx, ty in targets[:200]:
                d = abs(tx - nx) + abs(ty - ny)
                if d < dmin:
                    dmin = d
                    edmin = abs(tx - (w - 1) / 2) + abs(ty - (h - 1) / 2)
                elif d == dmin:
                    e = abs(tx - (w - 1) / 2) + abs(ty - (h - 1) / 2)
                    if e < edmin:
                        edmin = e
            score += -dmin * 2 - edmin * 0.01
        if dx == 0 and dy == 0:
            score -= 2
        if (nx, ny) in my_set:
            score -= 1  # discourage redundant moves inside already-owned area
        if score > best_score:
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]