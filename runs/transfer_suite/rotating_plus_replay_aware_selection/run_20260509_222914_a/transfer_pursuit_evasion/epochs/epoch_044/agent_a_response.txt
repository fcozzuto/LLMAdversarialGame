def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    self_role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in self_role) or ("runner" in self_role) or ("evasion" in self_role) or ("escape" in self_role)

    obs_list = observation.get("obstacles") or []
    obstacles = [(int(p[0]), int(p[1])) for p in obs_list if p and len(p) >= 2]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def obs_cost(x, y):
        if not obstacles:
            return 0.0
        dmin = 10**9
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < dmin:
                dmin = d
        if dmin <= 0:
            return 1e6
        if dmin == 1:
            return 220.0
        if dmin == 2:
            return 70.0
        return 1.0 / (dmin + 1.0)

    # If capture radius were >0, we'd handle, but here it's 0. Avoid immediate contact anyway.
    target_dist_sign = 1 if is_evader else -1
    best_dxdy = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        man = abs(nx - ox) + abs(ny - oy)
        # Prefer moving away/toward opponent deterministically.
        val = target_dist_sign * man
        val -= obs_cost(nx, ny)

        # Strongly avoid staying on opponent if that would be capture (radius 0).
        if nx == ox and ny == oy:
            val -= 1e7

        # Tie-break deterministically: lexicographic on (dx,dy) favoring earlier in moves list.
        if val > best_val:
            best_val = val
            best_dxdy = [dx, dy]

    return best_dxdy