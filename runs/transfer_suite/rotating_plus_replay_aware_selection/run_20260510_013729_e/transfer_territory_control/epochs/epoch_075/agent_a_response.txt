def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    x, y = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [0, 0]
    ox, oy = int(op[0]), int(op[1])

    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []
    obs_list = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []

    self_set = set((int(p[0]), int(p[1])) for p in self_t if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_set = set((int(p[0]), int(p[1])) for p in opp_t if isinstance(p, (list, tuple)) and len(p) >= 2)
    blocked = set((int(p[0]), int(p[1])) for p in obs_list if isinstance(p, (list, tuple)) and len(p) >= 2)

    targets = [(int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2]
    if not targets:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-break: fixed order in dirs.
    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue

        score = 0
        if (nx, ny) in opp_set:
            score += 120
        elif (nx, ny) in self_set:
            score += 8
        else:
            score += 55

        dist_opp = man((nx, ny), (ox, oy))
        score += dist_opp * 0.5  # spread out from opponent to reduce their ability to contest

        # Greedy move toward the nearest high-value frontier (unclaimed).
        nearest = 10**9
        nearest_edge = 10**9
        for tx, ty in targets:
            d = abs(tx - nx) + abs(ty - ny)
            if d < nearest:
                nearest = d
            edge_d = (tx if tx < w - 1 - tx else w - 1 - tx) + (ty if ty < h - 1 - ty else h - 1 - ty)
            # prefer cells nearer to board edges to widen territorial pressure
            if edge_d < nearest_edge:
                nearest_edge = edge_d
        score += (20 - nearest) * 3
        score += (-nearest_edge) * 0.1

        # Small penalty if we move away from our current closest unclaimed (encourage consistency).
        cur_nearest = 10**9
        for tx, ty in targets:
            d = abs(tx - x) + abs(ty - y)
            if d < cur_nearest:
                cur_nearest = d
        score -= max(0, nearest - cur_nearest) * 6

        key = (score, -dx, -dy)
        if score > best[0]:
            best = (score, dx, dy)

    if best[1] == 0 and best[2] == 0:
        # If all legal moves were blocked/out of bounds, stay.
        return [0, 0]
    return [int(best[1]), int(best[2])]