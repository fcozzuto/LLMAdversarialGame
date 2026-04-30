def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    obs_set = set((x, y) for x, y in obstacles)

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        for rx, ry in resources:
            ds = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(ry - oy)
            # Prefer resources where we're relatively closer; tie-break by our distance then deterministic order
            val = (do - ds)
            key = (-val, ds, rx, ry)  # smaller is better due to -val
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
        pref = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                d = abs(tx - nx) + abs(ty - ny)
                # Prefer moves that also move generally toward target deterministically
                toward = (dx == (0 if tx == sx else (1 if tx > sx else -1)) or dx == 0)
                pref.append((d, -toward, dx, dy))
        pref.sort()
        return [int(pref[0][2]), int(pref[0][3])] if pref else [0, 0]

    # No resources: move toward center while keeping safe
    cx, cy = (w - 1) // 2, (h - 1) // 2
    pref = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
            d = abs(cx - nx) + abs(cy - ny)
            pref.append((d, dx, dy))
    pref.sort()
    return [int(pref[0][1]), int(pref[0][2])] if pref else [0, 0]