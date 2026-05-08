def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best = None
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            val = -10**8
        else:
            # Base for where we end up (claiming happens on entry).
            if (nx, ny) in opp_terr:
                base = 6.5
            elif (nx, ny) in unclaimed:
                base = 3.0
            elif (nx, ny) in self_terr:
                base = 0.8
            else:
                base = 0.6

            # Resource attraction.
            if (nx, ny) in resources:
                base += 2.2

            # Pressure: prefer moves that reduce distance to opponent.
            d0 = abs(sx - ox) + abs(sy - oy)
            d1 = abs(nx - ox) + abs(ny - oy)
            pressure = 0.9 * (d0 - d1)

            # Keep away from opponent territory edges a bit (avoid getting trapped).
            opp_dist = min(abs(nx - x) + abs(ny - y) for (x, y) in opp_terr) if opp_terr else 10
            safety = 0.15 * opp_dist

            # Prefer expansion over staying still once we have some territory.
            still_pen = -0.3 if dx == 0 and dy == 0 else 0.0

            val = base + pressure + safety + still_pen

        if val > best_val:
            best_val = val
            best = [dx, dy]
        elif val == best_val and best is not None:
            # Deterministic tie-break: prefer non-stay, then lexicographically smallest move.
            if not (best[0] == 0 and best[1] == 0) and (dx == 0 and dy == 0):
                continue
            if (best[0] == 0 and best[1] == 0) and not (dx == 0 and dy == 0):
                best = [dx, dy]
            elif (dx, dy) < (best[0], best[1]):
                best = [dx, dy]

    dx, dy = int(best[0]), int(best[1])
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]