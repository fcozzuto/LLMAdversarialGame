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

    def dist8(a, b, c, d):
        dx = a - c
        dy = b - d
        ax = dx if dx >= 0 else -dx
        ay = dy if dy >= 0 else -dy
        return ax if ax > ay else ay

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        val = 0
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) in obs or not inb(rx, ry):
                continue
            d_ours = dist8(nx, ny, rx, ry)
            d_opp = dist8(ox, oy, rx, ry)
            row_bonus = 60 if ry == oy else 0
            y_adv = (abs(ry - oy) - abs(ry - ny)) * 8
            block = -20 if (abs(rx - nx) + abs(ry - ny) > abs(rx - sx) + abs(ry - sy)) else 0
            # If we can beat opponent, strongly favor; otherwise still move toward nearer-but-not-losing targets.
            val += (d_opp - d_ours) * 55 - d_ours * 2 + row_bonus + y_adv + block
        # If we are standing on/adjacent to a resource, prioritize immediate capture.
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) in obs or not inb(rx, ry):
                continue
            if rx == nx and ry == ny:
                val += 1000
            elif abs(rx - nx) <= 1 and abs(ry - ny) <= 1:
                val += 120
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]