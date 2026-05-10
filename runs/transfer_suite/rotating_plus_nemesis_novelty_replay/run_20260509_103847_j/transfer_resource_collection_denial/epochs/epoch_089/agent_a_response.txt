def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obstacles_list)
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_resource = None
    best_score = None
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        adv = do - ds  # positive => we are closer
        # Extra weight if resource lies on opponent's row/column line (often where denial pressure happens).
        line_bonus = 1.5 if (ry == oy or rx == ox) else 0.0
        # Prefer lower ds for stability, but mainly maximize advantage.
        score = adv * 10.0 + line_bonus - ds * 0.15
        if best_score is None or score > best_score:
            best_score = score
            best_resource = (rx, ry)

    tx, ty = best_resource

    best_move = (0, 0)
    best_val = None
    od0 = abs(tx - ox) + abs(ty - oy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds1 = abs(tx - nx) + abs(ty - ny)
        adv1 = od0 - ds1  # how much closer we are after move (vs opponent current pos)
        dist_pen = ds1 * 0.2
        # If staying still, penalize unless it keeps advantage and target is already reached.
        stay_pen = 3.0 if (dx == 0 and dy == 0 and ds1 > 0) else 0.0
        # Mildly avoid moving into the opponent's immediate neighborhood (denier often tries to swing).
        neigh_pen = 0.9 if (abs(nx - ox) <= 1 and abs(ny - oy) <= 1 and (nx != ox or ny != oy)) else 0.0
        val = adv1 * 12.0 + ( -dist_pen - stay_pen - neigh_pen )
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]