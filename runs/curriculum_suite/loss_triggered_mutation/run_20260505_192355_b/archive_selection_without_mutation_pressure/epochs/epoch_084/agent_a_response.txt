def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = -10**18

    # Opportunistic "intercept": for each move, consider the single most contested resource
    # (highest opponent lead, i.e., opponent closer) and maximize our resulting advantage.
    # Add a small bias toward moving closer to the chosen contested target to avoid dithering.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        best_adv = -10**18
        best_opp_lead = -10**18
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd  # positive: we are closer than opponent
            opp_lead = od - sd if od >= sd else -(sd - od)
            # Prefer resources where opponent is closer (higher od before we catch up)
            if od - md(ox, oy, rx, ry) != 0:
                pass
            if adv > best_adv:
                best_adv = adv
            if od - sd > best_opp_lead:
                best_opp_lead = od - sd

        # Tie-break: compute exact advantage vs the most "contested" resource (opponent closest).
        contested = resources[0]
        min_od = md(ox, oy, resources[0][0], resources[0][1])
        for rx, ry in resources[1:]:
            d = md(ox, oy, rx, ry)
            if d < min_od:
                min_od = d
                contested = (rx, ry)
        crx, cry = contested
        contested_sd = md(nx, ny, crx, cry)
        contested_adv = min_od - contested_sd

        val = best_adv * 1000 + contested_adv
        val += -contested_sd  # bias toward that target
        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best