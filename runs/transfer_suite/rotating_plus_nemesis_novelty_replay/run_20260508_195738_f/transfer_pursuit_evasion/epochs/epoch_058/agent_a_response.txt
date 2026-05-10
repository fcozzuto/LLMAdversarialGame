def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    is_evader = ("evad" in self_role) or (("agent" in self_role) and ("evad" in opp_role))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Desired step toward/away
    vx, vy = ox - sx, oy - sy
    if is_evader:
        vx, vy = -vx, -vy
    desx = 0 if vx == 0 else (1 if vx > 0 else -1)
    desy = 0 if vy == 0 else (1 if vy > 0 else -1)

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        d = dist2(nx, ny, ox, oy)
        # Pours: minimize distance; Evades: maximize distance.
        base = -d if not is_evader else d

        # Obstacle-aware tie-break: prefer moves that go away from nearby obstacles
        near = 0
        for ax, ay in obs:
            if abs(ax - nx) <= 1 and abs(ay - ny) <= 1:
                near += 1
        base -= near * (8 if not is_evader else -8)

        # Encourage following desired direction, but don't get stuck
        dir_pen = abs(dx - desx) + abs(dy - desy)
        base -= dir_pen * (3 if not is_evader else -3)

        # Slight center bias to reduce edge trapping
        center_pen = (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
        base -= center_pen * (0.2 if not is_evader else -0.2)

        if best is None or base > best_score or (base == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = base

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]