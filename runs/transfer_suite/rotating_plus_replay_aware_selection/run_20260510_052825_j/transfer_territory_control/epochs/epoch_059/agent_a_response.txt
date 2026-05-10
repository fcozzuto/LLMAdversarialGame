def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    if (not unclaimed) and (not oppT):
        return [0, 0]

    # Pick a deterministic target: nearest unclaimed, else nearest opponent cell.
    if unclaimed:
        targets = list(unclaimed)
        best_t = targets[0]
        best_td = 10**9
        for tx, ty in targets:
            d = abs(tx - x) + abs(ty - y)
            if d < best_td or (d == best_td and (ty, tx) < (best_t[1], best_t[0])):
                best_td = d
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        targets = list(oppT)
        best_t = targets[0]
        best_td = 10**9
        for tx, ty in targets:
            d = max(abs(tx - x), abs(ty - y))
            if d < best_td or (d == best_td and (ty, tx) < (best_t[1], best_t[0])):
                best_td = d
                best_t = (tx, ty)
        tx, ty = best_t

    def type_score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if (nx, ny) in unclaimed:
            return 7.0
        if (nx, ny) in oppT:
            return 4.5  # stepping into opponent territory is good when flipping is enabled
        if (nx, ny) in selfT:
            return 1.2
        return 0.3

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Encourage breaking through towards target; also prefer frontier adjacency to unclaimed.
        dist = max(abs(tx - nx), abs(ty - ny))
        val = type_score(nx, ny) - 0.9 * dist

        # Frontier pressure: count nearby unclaimed/opponent cells.
        adj_un = 0
        adj_opp = 0
        adj_self = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if 0 <= xx < w and 0 <= yy < h and (xx, yy) not in obstacles:
                    if (xx, yy) in unclaimed:
                        adj_un += 1
                    elif (xx, yy) in oppT:
                        adj_opp += 1
                    elif (xx, yy) in selfT:
                        adj_self += 1
        val += 0.25 * adj_un + 0.18 * adj_opp + 0.05 * adj_self

        if val > best_val or (val == best_val and (dy, dx) < (best_move[1], best_move[0])):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]