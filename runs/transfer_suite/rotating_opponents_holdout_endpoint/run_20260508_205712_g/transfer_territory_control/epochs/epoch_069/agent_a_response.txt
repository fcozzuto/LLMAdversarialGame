def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2 and p[0] is not None and p[1] is not None:
            obstacles.add((int(p[0]), int(p[1])))

    self_set = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_set = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    un_set = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    move_count = int(observation.get("turn_index", 0) or 0)

    # Deterministic mode switch: early take frontier; later press toward opponent side.
    early = move_count < 12

    best = (-(10**18), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        is_un = (nx, ny) in un_set
        is_opp = (nx, ny) in opp_set
        is_self = (nx, ny) in self_set

        # Heuristic: capture unclaimed, flip opponent when possible, avoid letting opponent get closer to our expansion.
        center_bias = -(abs(nx - cx) + abs(ny - cy))
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        dist_from_opp = dist_to_opp if early else dist_to_opp // 1

        # Prefer moving toward farthest-from-opponent unclaimed direction (guard against sweeper).
        # Also prefer approaching unclaimed near the center.
        score = 0
        score += 900000 if is_opp else 0
        score += 4000 if is_un else 0
        score += 120 if is_self else 0

        # Expansion: reward having more adjacent unclaimed after move.
        adj_un = 0
        adj_opp = 0
        for adx, ady in dirs:
            ax, ay = nx + adx, ny + ady
            if not inb(ax, ay) or (ax, ay) in obstacles:
                continue
            if (ax, ay) in un_set:
                adj_un += 1
            if (ax, ay) in opp_set:
                adj_opp += 1
        score += adj_un * 45
        score += adj_opp * (140 if not early else 60)

        # Territory holding: keep closer to center early, and keep distance from opponent later to prevent re-sweeps.
        score += center_bias * (3 if early else 1)
        score += dist_from_opp * (8 if early else -2)  # early: get away less; later: avoid opponent

        # Small deterministic tie-break favoring orthogonal moves first.
        ortho = 1 if (dx == 0 or dy == 0) else 0
        score += ortho * 2

        if score > best[0]:
            best = (score, dx, dy)

    if best[0] < -10**17:
        return [0, 0]
    return [int(best[1]), int(best[2])]