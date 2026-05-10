def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    self_ter = set(tuple(p) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_ter = set(tuple(p) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed_list = list(unclaimed)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_dist_to_unclaimed(x, y):
        if not unclaimed_list:
            return 999
        best = None
        for ux, uy in unclaimed_list:
            d = abs(ux - x) + abs(uy - y)
            if best is None or d < best:
                best = d
                if best == 0:
                    return 0
        return 999 if best is None else best

    def frontier_adj(x, y):
        # unclaimed adjacent to our territory
        for ax, ay in self_ter:
            if abs(ax - x) <= 1 and abs(ay - y) <= 1 and (ax != x or ay != y):
                return True
        return False

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        is_unclaimed = cell in unclaimed
        is_opp = cell in opp_ter
        is_self = cell in self_ter

        d_un = best_dist_to_unclaimed(nx, ny)
        # Deterministic, greedy expansion with contest preference
        score = 0
        if is_unclaimed:
            score += 1200
            if frontier_adj(nx, ny):
                score += 400
        elif is_opp:
            score += 750  # entering flips control
            if any(abs(px - nx) <= 1 and abs(py - ny) <= 1 for (px, py) in self_ter):
                score += 200
        elif is_self:
            score += 20
        else:
            score -= 50

        # Prefer moves that reduce distance to unclaimed
        score += (300 - 5 * d_un)
        # Mild preference to move toward center to avoid stagnation
        cx, cy = w // 2, h // 2
        score += -0.5 * (abs(nx - cx) + abs(ny - cy))
        # Avoid staying if another non-obstacle exists with equal/close gain
        if dx == 0 and dy == 0:
            score -= 5

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]