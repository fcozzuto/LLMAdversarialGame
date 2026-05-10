def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_terr.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not moves:
        return [0, 0]

    opp_center = (ox, oy)
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        dist_to_center = abs(nx - opp_center[0]) + abs(ny - opp_center[1])
        score = -dist_to_center

        if (nx, ny) in unclaimed:
            score += 6
        if (nx, ny) in opp_terr:
            score += 10  # likely flips on entry

        # Prefer moving toward nearest unclaimed/opp-territory, without expensive search
        nearest_bonus = 0
        if unclaimed:
            for tx, ty in unclaimed:
                d = abs(tx - nx) + abs(ty - ny)
                if d <= 4:
                    nearest_bonus = max(nearest_bonus, 3 - d)
        if opp_terr:
            for tx, ty in opp_terr:
                d = abs(tx - nx) + abs(ty - ny)
                if d <= 3:
                    nearest_bonus = max(nearest_bonus, 4 - d)
        score += nearest_bonus

        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]