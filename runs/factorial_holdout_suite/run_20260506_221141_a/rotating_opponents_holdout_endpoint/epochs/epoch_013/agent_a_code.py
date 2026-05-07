def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    deltas.sort(key=lambda t: (t[0], t[1]))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                score = -abs(nx - (w - 1 - sx)) - abs(ny - (h - 1 - sy))
                if best is None or score > best[0]:
                    best = (score, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    best_move = (-(10**9), 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        best_adv = -(10**6)
        nearest_self = 10**6
        nearest_opp = 10**6

        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            if sd < nearest_self:
                nearest_self = sd
            if od < nearest_opp:
                nearest_opp = od
            adv = od - sd  # positive means we are closer
            if adv > best_adv:
                best_adv = adv

        # Encourage grabbing resources where we are currently closer,
        # but discourage moves that give the opponent immediate races.
        race_penalty = 0
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            if od <= sd:
                # If opponent is not farther, reduce desirability.
                # Stronger penalty when they are much closer.
                if od < sd:
                    race_penalty += (sd - od + 1) * 2
                else:
                    race_penalty += 1

        score = best_adv * 50 - nearest_self - race_penalty
        if score > best_move[0]:
            best_move = (score, dx, dy)

    return [best_move[1], best_move[2]]