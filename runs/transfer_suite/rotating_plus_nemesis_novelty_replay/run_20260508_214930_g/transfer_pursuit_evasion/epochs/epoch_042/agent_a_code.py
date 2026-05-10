def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in self_role) or ("runner" in self_role) or ("escape" in self_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def wallness(x, y):
        # 0 near center, up to ~3 near corners
        d = min(x, y, w - 1 - x, h - 1 - y)
        return (3 - d) if d < 3 else 0

    # immediate capture (only possible if moving onto exact opponent cell)
    if not is_evader:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obs and nx == ox and ny == oy:
                return [dx, dy]

    best = None
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        ddx, ddy = nx - ox, ny - oy
        dist2 = ddx * ddx + ddy * ddy
        man = abs(ddx) + abs(ddy)
        if is_evader:
            # maximize distance; prefer using walls
            v = (dist2 * 1000) + (man * 10) + wallness(nx, ny)
            # also avoid stepping "behind" opponent too much: keep some directionality
            dir_same = (1 if (nx - sx) == 0 else 0) + (1 if (ny - sy) == 0 else 0)
            v -= dir_same
            better = (best_val is None) or (v > best_val)
        else:
            # minimize distance; prefer moving toward opponent's relative direction
            v = (-dist2 * 1000) + (-man * 10) - wallness(nx, ny) * 2
            step_toward = (1 if (nx != sx or ny != sy) else 0)
            v += step_toward
            better = (best_val is None) or (v > best_val)

        if better:
            best_val = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]