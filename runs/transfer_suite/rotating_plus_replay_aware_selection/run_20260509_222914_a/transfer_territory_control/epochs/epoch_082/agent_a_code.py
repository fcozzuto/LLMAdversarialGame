def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_ter = set(tuple(p) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_ter = set(tuple(p) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def nearest_unclaimed_dist(x, y):
        best = None
        for (ux, uy) in unclaimed:
            d = abs(ux - x) + abs(uy - y)
            if best is None or d < best:
                best = d
        return 999 if best is None else best

    def nearest_frontier_score(x, y):
        # Frontier cells are unclaimed adjacent to our territory
        best = None
        for (ax, ay) in self_ter:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = ax + dx, ay + dy
                    if inb(nx, ny) and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                        d = abs(nx - x) + abs(ny - y)
                        if best is None or d < best:
                            best = d
        return 10 if best is None else best

    # Precompute simple target preference
    frontier_dist = nearest_frontier_score(sx, sy)
    unclaimed_dist = nearest_unclaimed_dist(sx, sy)
    prefer_unclaimed = (frontier_dist <= 2) or (unclaimed_dist <= 3)

    best_move = (0, 0)
    best_val = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -10**8 if dx != 0 or dy != 0 else -10**7
        else:
            cell = (nx, ny)
            val = 0
            if cell in self_ter:
                val += 2
            if cell in unclaimed:
                val += 14 if prefer_unclaimed else 10
                val -= 0.5 * (abs(nx - sx) + abs(ny - sy))
            if cell in opp_ter:
                val += 9
            # Maintain pressure towards opponent general direction
            val += 0.06 * (ox - nx) * (1 if ox > sx else -1) + 0.06 * (oy - ny) * (1 if oy > sy else -1)
            # Penalize moving away from closest unclaimed
            val -= 0.25 * (nearest_unclaimed_dist(nx, ny) - unclaimed_dist)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]