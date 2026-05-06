def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # No known targets: move toward opponent if that might secure points by interaction.
        best = [0, 0]
        bd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = abs(nx - ox) + abs(ny - oy)
            if d < bd:
                bd = d
                best = [dx, dy]
        return best

    # Deterministic resource selection: consider top 3 resources by current advantage.
    scored = []
    for rx, ry in resources:
        adv = (abs(ox - rx) + abs(oy - ry)) - (abs(sx - rx) + abs(sy - ry))
        scored.append((adv, rx, ry))
    scored.sort(key=lambda t: (-t[0], t[1], t[2]))
    top = scored[:3]
    best_move = None
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0
        for _, rx, ry in top:
            myd = abs(nx - rx) + abs(ny - ry)
            opd = abs(ox - rx) + abs(oy - ry)
            val += opd - myd
        # Small tie-break for determinism: prefer smaller |dx| then smaller |dy| then lexicographic.
        tieb = (abs(dx), abs(dy), dx, dy)
        if val > best_val or (val == best_val and (best_move is None or tieb < (abs(best_move[0]), abs(best_move[1]), best_move[0], best_move[1]))):
            best_val = val
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move