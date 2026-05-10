def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()

    self_away = ("evader" in self_role) or ("runner" in self_role)
    opp_away = ("evader" in opp_role) or ("runner" in opp_role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_key = None

    def opp_best_dist(px, py):
        bestd = None
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                d = abs(nx - px) + abs(ny - py)
                if bestd is None:
                    bestd = d
                else:
                    if opp_away:
                        if d > bestd: bestd = d
                    else:
                        if d < bestd: bestd = d
        return bestd if bestd is not None else abs(ox - px) + abs(oy - py)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d_after = opp_best_dist(nx, ny)
        # If we are away: maximize distance; else minimize distance. Deterministic tie-break by (dx,dy) order.
        key = (-d_after, dx, dy) if self_away else (d_after, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]