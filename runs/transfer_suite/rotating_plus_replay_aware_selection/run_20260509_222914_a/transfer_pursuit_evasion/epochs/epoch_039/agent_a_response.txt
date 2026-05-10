def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("evasion" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def obs_pen(x, y):
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
            return 180.0
        return 14.0 / (dmin + 1)

    best = (-1e18, [0, 0])
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        dist = max(abs(nx - ox), abs(ny - oy))  # capture if dist==0
        # Heuristic: pursuer minimizes dist; evader maximizes dist.
        if is_evader:
            score = dist * 50.0 - obs_pen(nx, ny)
            # Prefer not to step into immediate "capture corridor": reduce likelihood of being diagonally aligned at distance 1.
            if max(abs(nx - ox), abs(ny - oy)) == 1:
                score -= 220.0
            # Also avoid edges only if they reduce escape options; but deterministic: mild edge penalty.
            score -= (0.5 if nx in (0, w - 1) or ny in (0, h - 1) else 0.0)
        else:
            score = (-dist) * 55.0 - obs_pen(nx, ny)
            if dist == 0:
                score += 1e6
            # Tighten zigzag chase: encourage moving in direction that reduces opponent-manifold.
            # Using Manhattan improvement as secondary tie-break.
            score += (abs(sx - ox) + abs(sy - oy) - (abs(nx - ox) + abs(ny - oy))) * 3.0
            # Mild preference to keep line progress: penalize moves that reverse both x and y.
            if (nx - sx) * (sx - ox) < 0 and (ny - sy) * (sy - oy) < 0:
                score -= 6.0

        if score > best[0]:
            best = (score, [dx, dy])

    return best[1]