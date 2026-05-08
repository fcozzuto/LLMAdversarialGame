def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (dx != 0 or dy != 0) and inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy))
    moves.append((0, 0))
    if not moves:
        return [0, 0]

    if not resources:
        tx = w - 1 if ox < w // 2 else 0
        ty = h - 1 if oy < h // 2 else 0
        best = min(moves, key=lambda m: md(sx + m[0], sy + m[1], tx, ty))
        return [int(best[0]), int(best[1])]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy

        # Choose the resource that maximizes our relative progress vs opponent.
        chosen = None
        chosen_adv = -10**18
        chosen_ours = 10**9
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            ours = md(nx, ny, rx, ry)
            oppd = md(ox, oy, rx, ry)
            adv = oppd - ours
            if adv > chosen_adv or (adv == chosen_adv and (ours < chosen_ours or (ours == chosen_ours and (rx, ry) < (chosen[0], chosen[1])))):
                chosen_adv = adv
                chosen_ours = ours
                chosen = (rx, ry, ours, oppd)

        if chosen is None:
            val = -md(nx, ny, w - 1, h - 1)
        else:
            rx, ry, ours, oppd = chosen
            # Prefer winning races: higher advantage and smaller our distance.
            val = (chosen_adv * 20) - ours
            # If opponent is extremely close to the chosen resource, prioritize reducing that race.
            if oppd == 1:
                val += 30
            if oppd == 0:
                val -= 50  # likely too late

            # Small tie-break: reduce distance to the nearest resource overall.
            nearest = min(md(nx, ny, r[0], r[1]) for r in resources if (r[0], r[1]) not in obs) if resources else 0
            val += max(0, 10 - nearest) * 0.1

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]