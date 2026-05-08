def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    oxp, oyp = map(int, observation.get("opponent_position") or (w - 1, h - 1))
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    un_list = list(unclaimed)
    if un_list:
        min_un_dist = min(abs(x - sx) + abs(y - sy) for x, y in un_list)
    else:
        min_un_dist = 999999

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = None
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if (nx, ny) in selfT:
            tscore = -2.0
        elif (nx, ny) in unclaimed:
            tscore = 5.0
        elif (nx, ny) in oppT:
            tscore = 2.8
        else:
            tscore = 0.0

        if un_list:
            d_un = min(abs(x - nx) + abs(y - ny) for x, y in un_list)
        else:
            d_un = 0.0

        d_center = abs(nx - cx) + abs(ny - cy)
        d_opp = abs(nx - oxp) + abs(ny - oyp)

        key = (
            -(tscore * 10.0),                # prefer unclaimed/opponent entries
            d_un,                           # then go nearest unclaimed
            d_center,                       # then toward center
            -d_opp,                         # then away from opponent to reduce their pressure
            dx, dy                          # deterministic tie-break
        )
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]