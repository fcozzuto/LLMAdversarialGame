def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        for dx, dy in [(0, 0),(1, 1),(1, 0),(0, 1),(-1, 1),(-1, 0),(0, -1),(1, -1),(-1, -1)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    res_set = set(tuple(p) for p in resources)
    dirs = [(0,0),(1,0),(0,1),(-1,0),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]

    best = None
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in res_set:
            val = 10**6
        else:
            # Resource race: prioritize resources we can reach sooner than opponent.
            val = 0
            min_my = 10**9
            min_opp = 10**9
            for rx, ry in res_set:
                myd = abs(nx - rx) + abs(ny - ry)
                opd = abs(ox - rx) + abs(oy - ry)
                if myd < min_my:
                    min_my = myd
                if opd < min_opp:
                    min_opp = opd
                # Prefer resources where we're closer (denier opponent).
                val += (opd - myd) * 10 - myd
            # Encourage general progress to any resource and slight distance from opponent.
            val += (min_opp - min_my) * 5
            val -= (abs(nx - ox) + abs(ny - oy)) * 2

        # Small tie-breaker: center-ish to reduce corner stagnation
        val -= (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)) * 0.001
        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best