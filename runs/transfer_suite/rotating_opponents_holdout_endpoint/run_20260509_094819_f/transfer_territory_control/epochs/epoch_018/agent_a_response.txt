def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    if isinstance(unclaimed, dict):
        unclaimed = list(unclaimed.keys())
    unclaimed_set = set(tuple(p) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Aggression: if we're behind, try to flip opponent cells; if ahead, expand cautiously.
    sc = int(observation.get("self_territory_count", 0))
    oc = int(observation.get("opponent_territory_count", 0))
    aggressive = sc <= oc

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Frontier targets: unclaimed adjacent to opponent territory to pull the center-claimer.
    opp_frontier = set()
    for (x, y) in opp_terr:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed_set and (nx, ny) not in obstacles:
                opp_frontier.add((nx, ny))

    def score_cell(nx, ny):
        if (nx, ny) in obstacles or not inb(nx, ny):
            return -10**9
        s = 0.0
        if (nx, ny) in unclaimed_set:
            s += 5.0
        if (nx, ny) in self_terr:
            s += 1.0 if not aggressive else 0.6
        if (nx, ny) in opp_terr:
            s += 3.5 if aggressive else -2.0  # don't dive unless we need to
        # Encourage pushing toward opponent-frontier; otherwise toward center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        target_list = list(opp_frontier) if opp_frontier else []
        if target_list:
            # nearest frontier distance (no full search beyond targets set)
            dmin = 10**9
            for tx, ty in target_list:
                d = abs(tx - nx) + abs(ty - ny)
                if d < dmin:
                    dmin = d
            s += 3.5 / (1 + dmin)
        else:
            dcen = abs(nx - cx) + abs(ny - cy)
            s += 1.5 / (1 + dcen)
        # Slightly prefer moving away from obstacles' immediate corners (deterministic, cheap).
        for ox, oy in obstacles:
            if abs(ox - nx) <= 1 and abs(oy - ny) <= 1:
                s -= 0.8
        return s

    best = (sx, sy)
    best_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        s = score_cell(nx, ny)
        # tie-break deterministically by (dx,dy) order already fixed
        if s > best_s:
            best_s = s
            best = (nx, ny)

    return [best[0] - sx, best[1] - sy]