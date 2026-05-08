def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    def to_set(key):
        out = set()
        cells = observation.get(key) or []
        for p in cells:
            if p is None:
                continue
            if isinstance(p, dict):
                x, y = p.get("x", p.get(0)), p.get("y", p.get(1))
            elif isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
            else:
                continue
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                out.add((x, y))
        return out

    obstacles = to_set("obstacles") | to_set("resource_obstacles")
    unclaimed = to_set("unclaimed_cells") | to_set("unclaimed") | to_set("neutral_cells")
    opp_terr = to_set("opponent_territory")
    resources = to_set("resources") | to_set("resource_cells") | to_set("resource_locations")

    targets = unclaimed if unclaimed else (opp_terr if opp_terr else resources)
    if not targets:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    targets_list = list(targets)
    # Keep only a small deterministic shortlist
    scored = []
    for (tx, ty) in targets_list:
        d = (tx - sx) * (tx - sx) + (ty - sy) * (ty - sy)
        scored.append((d, tx, ty))
    scored.sort()
    shortlist = [(tx, ty) for _, tx, ty in scored[:20]]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        is_un = (nx, ny) in unclaimed
        is_opp = (nx, ny) in opp_terr
        # Heuristic: claim/flip first, then move toward best target, then toward center
        # Deterministic tie-break uses (score, -dx, -dy, nx, ny)
        mind = 10**9
        for (tx, ty) in shortlist:
            dd = abs(tx - nx) + abs(ty - ny)
            if dd < mind:
                mind = dd
        center = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        score = 0
        if is_un:
            score += 120
        if is_opp:
            score += 80
        score += -mind
        score += -0.05 * center
        key = (-score, -dx, -dy, nx, ny)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]