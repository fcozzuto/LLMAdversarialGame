def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def dist8(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-(10**18), 0, 0)

    # Deterministic tie-breaker: later moves in list if equal? use fixed ordering by preferring earlier.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # If landing on a resource this turn, do it.
        landing = 1 if any(int(r[0]) == nx and int(r[1]) == ny for r in resources) else 0
        best_target = -(10**18)

        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if not inb(rx, ry) or (rx, ry) in obs:
                continue
            d_ours = dist8(nx, ny, rx, ry)
            d_opp = dist8(ox, oy, rx, ry)
            # Prefer immediate capture, then contested wins, then shortest progress.
            val = 0
            if d_ours == 0:
                val += 10**6
            val += (d_opp - d_ours) * 1200
            val -= d_ours * 25
            # Small reward for going toward resources that opponent is also close to (to create contests).
            val += (40 if d_opp <= 2 else 0)
            if val > best_target:
                best_target = val

        # Slightly prefer moves that don't increase distance to best target too much.
        total = best_target + (landing * 5000)
        if total > best[0]:
            best = (total, dx, dy)

    return [int(best[1]), int(best[2])]