def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in self_role) or ("runner" in self_role) or ("evasion" in self_role) or ("escape" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-break: prefer staying on relevant axis then towards opponent/away from opponent
    pref = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    pref_set = set(pref)
    ordered = pref + [m for m in moves if m not in pref_set]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def min_obs_dist(x, y):
        if not obstacles:
            return 999
        best = 999
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    best_val = None
    best_move = (0, 0)

    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        dist = max(abs(nx - ox), abs(ny - oy))  # capture radius is 0; use Chebyshev
        obst_d = min_obs_dist(nx, ny)

        # Also add slight preference to reduce/avoid "cornering" by obstacles: keep away from obstacles
        if is_evader:
            val = (dist * 1000) + (obst_d * 10) + (nx + ny) * 0.001
        else:
            val = (-dist * 1000) + (obst_d * 10) + (nx - ny) * 0.001

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]