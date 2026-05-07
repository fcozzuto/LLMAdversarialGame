def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    moves = [(dx, dy) for dx, dy in dirs if valid(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    # Manhattan distance
    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    # Deterministic move scoring: win-first (collect or beat opponent), then advance to best contested resource.
    best = None
    best_val = None
    opp_turn_adv = man(ox, oy, ox, oy)  # always 0, kept deterministic
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        val = 0
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            if sd == 0:
                val += 1000000  # immediate collection
            else:
                # If we can reach not later than opponent, prioritize strongly; otherwise penalize.
                if sd <= od:
                    gap = od - sd  # >=0
                    val += 20000 + gap * 500
                else:
                    val -= 8000 + (sd - od) * 600

                # Prefer reducing distance overall
                val += (1000 // (sd + 1)) - (200 // (od + 1)) + opp_turn_adv

        # Small tie-break: prefer moving toward the currently closest resource from our next position
        if resources:
            md = min(man(nx, ny, rx, ry) for rx, ry in resources if (rx, ry) not in obstacles)
            val -= md * 3

        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]