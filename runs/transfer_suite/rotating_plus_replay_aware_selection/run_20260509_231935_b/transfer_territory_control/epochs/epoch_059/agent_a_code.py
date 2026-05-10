def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    t = int(observation.get("turn_index", 0))
    k = t % 9
    dirs = dirs[k:] + dirs[:k]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    center_x, center_y = (w - 1) // 2, (h - 1) // 2

    if unclaimed:
        def target_score(p):
            x, y = p
            edge = (x == 0 or x == w - 1 or y == 0 or y == h - 1)
            near_opp = man(x, y, ox, oy)
            dist = man(x, y, sx, sy)
            return (dist - 2.0 * edge) + 0.2 * near_opp - 0.01 * (abs(x - center_x) + abs(y - center_y))
        target = min(unclaimed, key=target_score)
    else:
        candidates = list(opp_terr) + list(self_terr)
        if not candidates:
            tx, ty = center_x, center_y
        else:
            tx, ty = min(candidates, key=lambda p: man(sx, sy, p[0], p[1]))
        target = [tx, ty]

    tx, ty = target

    best = (float("-inf"), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        dist_to_target = man(nx, ny, tx, ty)
        dist_to_opp = man(nx, ny, ox, oy)
        edge = 1 if (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1) else 0
        toward_target = 1 if dist_to_target < man(sx, sy, tx, ty) else 0

        flip = 1 if (nx, ny) in opp_terr else 0
        stay_claimed = 1 if (nx, ny) in self_terr else 0

        # Encourage taking enemy cells when possible, otherwise press frontier unclaimed/edges toward target.
        val = 3.5 * flip + 0.8 * toward_target + 0.35 * edge - 0.08 * dist_to_target + 0.02 * dist_to_opp + 0.15 * stay_claimed
        # Deterministic tie-break: prefer moves with smaller dx, then smaller dy, then closer to target.
        tiebreak = (-dx, -dy, dist_to_target)
        if (val, -dist_to_target, tiebreak) > (best[0], -best[2], (0, 0, 0)):
            best = (val, dx, dy)

    return [int(best[1]), int(best[2])]