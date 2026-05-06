def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = md(nx, ny, tx, ty)
            key = (d, md(nx, ny, ox, oy))
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    remaining = observation.get("remaining_resource_count", len(resources))
    contest_bias = 3 if remaining <= 3 else 1

    best_key = None
    best_move = (0, 0)
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        closest_self = 10**9
        closest_opp = 10**9
        best_adv = -10**18
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            closest_self = sd if sd < closest_self else closest_self
            closest_opp = od if od < closest_opp else closest_opp
            adv = (od - sd)  # positive means resource closer to self than opponent
            if adv > best_adv:
                best_adv = adv
        dist_to_opp = md(nx, ny, ox, oy)
        # Prefer creating advantage; also nudge toward the opponent when we're not ahead.
        score = best_adv * 1000 - closest_self - contest_bias * dist_to_opp
        # Deterministic tie-break: smaller (self dist) then (opp dist) then move ordering implicit via iteration.
        tie = (-(best_adv * 1000), closest_self, dist_to_opp, dx, dy)
        key = (score, -tie[0], tie)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]