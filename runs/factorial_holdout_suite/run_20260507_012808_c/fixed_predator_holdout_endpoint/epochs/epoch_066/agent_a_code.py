def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    valid = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                valid.append((x, y))
    if not valid:
        return [0, 0]

    # Resource contest heuristic: prioritize where opponent is farther than us, but still favor being close.
    best = None
    best_key = None
    for x, y in valid:
        sd = abs(x - sx) + abs(y - sy)
        od = abs(x - ox) + abs(y - oy)
        race = od - sd  # positive: we are closer
        key = (race, -sd, -od)  # lexicographic max
        if best_key is None or key > best_key:
            best_key = key
            best = (x, y)

    tx, ty = best

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Move one step toward target while avoiding obstacles.
    best_move = [0, 0]
    best_mscore = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            dist = abs(tx - nx) + abs(ty - ny)
            opp_dist = abs(tx - ox) + abs(ty - oy)
            # Slightly prefer moves that also increase separation from opponent target pressure.
            mscore = (-dist, -opp_dist, -abs((sx - ox) - (nx - ox)))
            if best_mscore is None or mscore > best_mscore:
                best_mscore = mscore
                best_move = [dx, dy]

    return best_move if best_mscore is not None else [0, 0]