def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        dx = 1 if sx < w - 1 else (-1 if sx > 0 else 0)
        dy = 1 if sy < h - 1 else (-1 if sy > 0 else 0)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        return [0, 0]

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    opp_d_to = d2(sx, sy, ox, oy)
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Choose target that we reach sooner than opponent, with extra anti-crowding.
        local_best = -10**18
        for rx, ry in resources:
            sd = d2(nx, ny, rx, ry)
            od = d2(ox, oy, rx, ry)
            if sd == 0:
                val = 10**7
            else:
                # prioritize "winnable" resources and moving toward them; penalize moving near opponent
                val = (od - sd) * 1000 - sd - d2(nx, ny, ox, oy) * 2
            # slight determinism: break ties by coordinate pattern
            val -= (rx * 3 + ry * 5) * 0.001
            if val > local_best:
                local_best = val

        # If opponent is extremely close, prioritize distancing while still keeping a decent target
        dist_to_opp = d2(nx, ny, ox, oy)
        anti_opp = (opp_d_to - dist_to_opp)  # positive if we get closer; we'd rather avoid that
        val = local_best - max(0, anti_opp) * 50 + dist_to_opp * 0.01
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move == (0, 0):
        # fallback: step to maximize distance from opponent while avoiding obstacles
        best = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = d2(nx, ny, ox, oy) - d2(nx, ny, resources[0][0], resources[0][1]) * 0.01
            if v > best:
                best = v
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]