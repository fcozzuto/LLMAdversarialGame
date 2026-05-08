def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Priority targets: unclaimed cells near our frontier; else nearest unclaimed; else center
    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed_set = set((int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) == 2)
    self_terr = observation.get("self_territory") or []
    self_terr_set = set((int(p[0]), int(p[1])) for p in self_terr if isinstance(p, (list, tuple)) and len(p) == 2)

    frontier = []
    if self_terr_set and unclaimed_set:
        for (x, y) in self_terr_set:
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if (nx, ny) in unclaimed_set:
                    frontier.append((nx, ny))
        if frontier:
            targets = frontier
        else:
            targets = list(unclaimed_set)
    else:
        targets = list(unclaimed_set)

    if not targets:
        targets = [(w // 2, h // 2)]

    cx, cy = w / 2.0, h / 2.0
    # Order targets deterministically: closest to us, then closer to center
    targets.sort(key=lambda t: (man(sx, sy, t[0], t[1]), (t[0] - cx) ** 2 + (t[1] - cy) ** 2, t[0], t[1]))

    # Choose move by maximizing a local heuristic that favors claiming/approaching target and cutting opponent
    best = None
    best_val = -10**18

    # Precompute opponent distance baseline
    d_opp_before = man(sx, sy, ox, oy)
    d_center_before = abs(sx - cx) + abs(sy - cy)

    # Consider top few targets to keep deterministic and simple
    for tx, ty in targets[:6]:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue

            # Claim pressure: closer to target
            d_t_before = man(sx, sy, tx, ty)
            d_t_after = man(nx, ny, tx, ty)
            claim = d_t_before - d_t_after

            # Territory contest: move to reduce opponent distance (helps flipping when enabled)
            d_opp_after = man(nx, ny, ox, oy)
            opp = d_opp_before - d_opp_after

            # Centering: avoid getting stuck in corners late; keep moderate weight
            d_center_after = abs(nx - cx) + abs(ny - cy)
            center = d_center_before - d_center_after

            # Slight preference for moves that step into unclaimed (since entering opponent-owned flips, unclaimed is still useful)
            unclaimed_bonus = 1 if (nx, ny) in unclaimed_set else 0

            val = 5 * claim + 3 * opp + 0.5 * center + 2 * unclaimed_bonus

            # Tie-break deterministically by direction order and coordinates
            if best is None or val > best_val or (val == best_val and (dx, dy) < best):
                best_val = val
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]