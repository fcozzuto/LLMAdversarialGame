def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles if len(p) >= 2)

    self_terr = set(observation.get("self_territory") or [])
    opp_terr = set(observation.get("opponent_territory") or [])
    unclaimed = observation.get("unclaimed_cells") or []

    resources = observation.get("resources") or []
    remaining = observation.get("remaining_resource_count", None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def neigh_moves():
        return [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    # Pick deterministic target
    target = None
    res_list = []
    if resources and (remaining is None or remaining > 0):
        res_list = [(p[0], p[1]) for p in resources if len(p) >= 2]
    if res_list:
        res_list.sort(key=lambda c: (manh(sx, sy, c[0], c[1]), c[0], c[1]))
        target = res_list[0]
    else:
        un_list = [(p[0], p[1]) for p in unclaimed if len(p) >= 2]
        # Prefer unclaimed near opponent, else near self
        un_list.sort(key=lambda c: (manh(ox, oy, c[0], c[1]) * 3 + manh(sx, sy, c[0], c[1]), c[0], c[1]))
        target = un_list[0] if un_list else (ox, oy)

    best = None
    best_score = -10**18
    for dx, dy in neigh_moves():
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Score: approach target, avoid opponent proximity, prefer expanding territory/unclaimed
        score = -manh(nx, ny, target[0], target[1])
        d_opp = manh(nx, ny, ox, oy)
        score += d_opp * 0.2
        if (nx, ny) in unclaimed:
            score += 2.0
        if (nx, ny) in opp_terr:
            score -= 0.5
        if (nx, ny) in self_terr:
            score += 0.5
        # Tie-break deterministically
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]