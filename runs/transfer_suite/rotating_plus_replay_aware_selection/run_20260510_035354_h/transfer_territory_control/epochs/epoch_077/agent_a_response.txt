def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []
    resources = observation.get("resources") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obset = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}
    selfset = {(p[0], p[1]) for p in self_terr if isinstance(p, (list, tuple)) and len(p) >= 2}
    oppset = {(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2}

    unclaimed_list = [(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2 and (p[0], p[1]) not in obset]
    opp_list = [(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2 and (p[0], p[1]) not in obset]

    targets = []
    if unclaimed_list:
        targets.extend(unclaimed_list)
    if opp_list:
        targets.extend(opp_list)

    if not targets:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]

    # Prefer stealing/claiming: opponent territory is weighted more than unclaimed.
    best_move = (0, 0)
    best_score = -10**18

    def dist(x1, y1, x2, y2):
        d1 = x1 - x2
        if d1 < 0:
            d1 = -d1
        d2 = y1 - y2
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    # Precompute closest target distance for speed
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obset:
            continue
        # Skip moves that trap us away from both frontiers (small penalty)
        score = 0
        on_opp = (nx, ny) in oppset
        score += 6 if on_opp else 0
        on_un = (nx, ny) in {(p[0], p[1]) for p in unclaimed_list}
        score += 3 if on_un else 0
        # Encourage expansion away from own dense area slightly (avoid dithering)
        score -= 1 if (nx, ny) in selfset else 0

        # Frontier proximity: closest target after move
        md = 10**9
        for tx, ty in targets:
            d = dist(nx, ny, tx, ty)
            if d < md:
                md = d
                if md == 0:
                    break
        score += -md

        # Avoid stepping into immediate obstacle pinch
        pinch = 0
        for sx, sy in neigh8:
            xx, yy = nx + sx, ny + sy
            if inb(xx, yy) and (xx, yy) in obset:
                pinch += 1
        score -= pinch * 0.2

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]