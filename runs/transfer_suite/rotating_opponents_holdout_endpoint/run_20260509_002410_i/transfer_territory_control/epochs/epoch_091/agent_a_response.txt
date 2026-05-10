def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_t = set(tuple(map(int, p)) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_t = set(tuple(map(int, p)) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(map(int, p)) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    opp_list = list(opp_t)
    un_list = list(unclaimed)
    near_opp_cache = {}
    near_un_cache = {}

    def nearest_sq(srcx, srcy, pts, cache):
        key = (srcx, srcy)
        if key in cache:
            return cache[key]
        best = None
        for x, y in pts:
            dx, dy = x - srcx, y - srcy
            d = dx * dx + dy * dy
            if best is None or d < best:
                best = d
        if best is None:
            best = (w * w + h * h)
        cache[key] = best
        return best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        dcenter = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        dopp = nearest_sq(nx, ny, opp_list, near_opp_cache) if opp_list else (w * w + h * h)
        dun = nearest_sq(nx, ny, un_list, near_un_cache) if un_list else (w * w + h * h)

        if (nx, ny) in opp_t:
            gain = -5.5  # strong preference to flip/expand into opponent control
        elif (nx, ny) in unclaimed:
            gain = -2.0
        elif (nx, ny) in self_t:
            gain = 0.5
        else:
            gain = 0.8

        # Favor center + approaching unclaimed; also sometimes approach opponent to counterclaim.
        score = gain + 0.025 * dcenter + 0.012 * dun - 0.010 * (w * w + h * h - dopp) / (w * w + h * h)

        if best is None or (score < best[0]) or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]