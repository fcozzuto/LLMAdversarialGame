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
    d0 = (0 if sx == ox else 1 if ox > sx else -1, 0 if sy == oy else 1 if oy > sy else -1)

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def obs_clear(nx, ny):
        if (nx, ny) in obs:
            return None
        if w <= 2 or h <= 2:
            return 0
        # small penalty if next cell adjacent to obstacle (encourages pathing around obstacles)
        m = 0
        for (x, y) in obs:
            ad = abs(nx - x) + abs(ny - y)
            if ad == 0:
                return None
            if ad == 1:
                m += 1
        return m

    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        oc = obs_clear(nx, ny)
        if oc is None:
            continue

        dd = dist2(nx, ny, ox, oy)
        # deterministic tie-break favoring diagonal and forward-ish movement
        diag = 1 if dx != 0 and dy != 0 else 0
        toward = 1 if (dx == d0[0] or dy == d0[1]) else 0
        if is_evader:
            val = (dd * 4) - (oc * 2) + (diag * 0.01) + (toward * 0.005) - (dx == 0 and dy == 0) * 0.02
        else:
            val = (-dd * 4) - (oc * 2) + (diag * 0.01) + (toward * 0.005) - (dx == 0 and dy == 0) * 0.02

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]