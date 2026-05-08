def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in (observation.get("self_territory") or []):
        self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in (observation.get("opponent_territory") or []):
        opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            x, y = sx + dx, sy + dy
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                moves.append((dx, dy, x, y))
    moves.append((0, 0, sx, sy))

    def step_toward(tx, ty, ex, ey):
        dx = 0 if tx == ex else (1 if tx > ex else -1)
        dy = 0 if ty == ey else (1 if ty > ey else -1)
        nx, ny = ex + dx, ey + dy
        if (dx, dy) == (0, 0) or not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            best = None
            for ddx, ddy, x2, y2 in moves:
                dist = abs(tx - x2) + abs(ty - y2)
                if best is None or dist < best[0] or (dist == best[0] and (ddx, ddy) < best[1]):
                    best = (dist, (ddx, ddy))
            return list(best[1]) if best else [0, 0]
        return [dx, dy]

    target = None
    best = None
    if unclaimed:
        # Prefer unclaimed near our side and far from opponent; break ties deterministically.
        for i in range(min(48, len(unclaimed))):
            x, y = int(unclaimed[i][0]), int(unclaimed[i][1])
            if (x, y) in obstacles:
                continue
            d_self = abs(x - sx) + abs(y - sy)
            d_opp = abs(x - ox) + abs(y - oy)
            # Prefer cells likely to be reachable soon and that push away from opponent.
            val = (3 * d_opp) - (2 * d_self) - 0.01 * (x + 7 * y)
            if target is None or val > best:
                target = (x, y)
                best = val
        # If too far, still steer to reduce distance.
        if target is None:
            target = (sx, sy)
    else:
        # Fallback: expand into adjacent unclaimed or safest frontier near our territory.
        candidates = []
        for ddx, ddy, nx, ny in moves:
            if (nx, ny) in obstacles:
                continue
            is_unclaimed = True
            if (nx, ny) in self_terr:
                is_unclaimed = False
            if (nx, ny) in opp_terr:
                is_unclaimed = True
            # Prefer attacking/claiming opponent boundary more than wandering.
            score = (2 if is_unclaimed else 0) - (abs(nx - ox) + abs(ny - oy)) * 0.01
            candidates.append((score, (ddx, ddy)))
        return list(min(candidates, key=lambda t: (-t[0], t[1]))[1]) if candidates else [0, 0]

    tx, ty = target[0], target[1]
    return step_toward(tx, ty, sx, sy)