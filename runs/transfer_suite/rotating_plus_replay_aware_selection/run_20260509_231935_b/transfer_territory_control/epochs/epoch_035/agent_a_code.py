def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]
    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    unclaimed_set = set(unclaimed)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    candidates = []
    if self_terr and unclaimed:
        neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        targets = []
        for tx, ty in unclaimed:
            for dx, dy in neigh:
                if (tx + dx, ty + dy) in self_terr:
                    targets.append((tx, ty))
                    break
        if targets:
            unclaimed = targets

    if unclaimed:
        best = None
        for tx, ty in unclaimed:
            d = abs(tx - sx) + abs(ty - sy)
            if best is None or d < best[0] or (d == best[0] and (tx, ty) < best[1]):
                best = (d, (tx, ty))
        tx, ty = best[1]
        for dx, dy in dirs8 + [(0, 0)]:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles or (nx, ny) not in unclaimed_set and unclaimed_set:
                continue
            score = abs(tx - nx) + abs(ty - ny)
            candidates.append((score, dx, dy))
        if candidates:
            candidates.sort(key=lambda x: (x[0], x[1], x[2]))
            return [candidates[0][1], candidates[0][2]]

    opp = observation.get("opponent_position")
    if opp is not None:
        ox, oy = opp
        bestd = None
        bestmove = (0, 0)
        for dx, dy in dirs8 + [(0, 0)]:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = abs(ox - nx) + abs(oy - ny)
            if bestd is None or d < bestd or (d == bestd and (dx, dy) < bestmove):
                bestd = d
                bestmove = (dx, dy)
        return [bestmove[0], bestmove[1]]

    return [0, 0]