def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    steps = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    if not valid(sx, sy):
        return [0, 0]

    unclaimed = observation.get("unclaimed_cells") or []
    cand = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                cand.append((x, y))
    if not cand:
        cand = [(x, y) for x in range(w) for y in range(h) if (x, y) not in obs]

    def score_cell(tx, ty):
        dapp = abs(tx - ox) + abs(ty - oy)  # prefer far from opponent
        ds = abs(tx - sx) + abs(ty - sy)    # prefer closer to expand
        return dapp * 10 - ds

    best_dir = [0, 0]
    best_val = -10**18
    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = 0
        # Prefer stepping into the best nearby unclaimed cells (sample for speed)
        for tx, ty in cand[::max(1, len(cand)//30)][:30]:
            if abs(tx - nx) + abs(ty - ny) <= 6:
                val += score_cell(tx, ty)
        # If no nearby candidates, still keep opponent-distance as fallback
        if val == 0:
            val = (abs(nx - ox) + abs(ny - oy)) * 10 - (abs(nx - sx) + abs(ny - sy))
        if val > best_val or (val == best_val and (dx, dy) < (best_dir[0], best_dir[1])):
            best_val = val
            best_dir = [dx, dy]
    return best_dir