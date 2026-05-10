def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    neigh8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    opp = observation.get("opponent_territory") or []
    opp_set = set()
    for p in opp:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_set.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    cand = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                for dx, dy in neigh8:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in opp_set:
                        cand.append((x, y))
                        break

    if not cand:
        for p in unclaimed:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y):
                    cand.append((x, y))

    dirs = neigh8
    self_terr = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                self_terr.add((x, y))

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        target = None
        if cand:
            target = min(cand, key=lambda t: (abs(t[0] - nx) + abs(t[1] - ny), abs(t[0] - ox) + abs(t[1] - oy), t[0], t[1]))
        else:
            target = min([(ox, oy)], key=lambda t: abs(t[0] - nx) + abs(t[1] - ny))

        dist_to_target = abs(target[0] - nx) + abs(target[1] - ny)
        dist_to_opp = abs(ox - nx) + abs(oy - ny)
        in_opp = (nx, ny) in opp_set
        in_self = (nx, ny) in self_terr
        edge_pressure = 0
        for ddx, ddy in neigh8:
            ax, ay = nx + ddx, ny + ddy
            if (ax, ay) in opp_set:
                edge_pressure += 1

        # Prefer invading opponent/edge, then closeness to edge targets, and avoid moving deep into own territory.
        score = (0 if in_opp else 1,
                 dist_to_target,
                 -edge_pressure,
                 dist_to_opp,
                 0 if in_self else 1)

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]