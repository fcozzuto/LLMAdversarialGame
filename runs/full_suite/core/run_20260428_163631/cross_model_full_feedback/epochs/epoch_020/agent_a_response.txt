def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            px, py = int(p[0]), int(p[1])
            if inb(px, py): obstacles.add((px, py))
        except: pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obstacles:
                resources.append((rx, ry))
        except: pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        ax, ay, bx, by = abs(ax - bx), abs(ay - by), 0, 0
        return max(ax, ay)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = legal[0]
    best_val = -10**18

    for dx, dy, nx, ny in legal:
        # Base: prefer moving toward center a bit
        val = -0.15 * cheb(nx, ny, int(round(cx)), int(round(cy)))

        # Try to secure a resource where we can be (or stay) closer than opponent
        if resources:
            # Also encourage picking a nearer resource than opponent would
            nearest_opp_gap = None
            for rx, ry in resources:
                d_self = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                gap = d_opp - d_self  # positive => we are closer now
                # Main: prioritize positive gaps, then smaller own distance
                if nearest_opp_gap is None or gap > nearest_opp_gap:
                    nearest_opp_gap = gap
                if gap >= 0:
                    val += 50 + 6 * gap - 2 * d_self
                else:
                    val += 4 * gap - 0.7 * d_self

            # If we can be much closer to some resource, boost; else avoid getting "trapped"
            if nearest_opp_gap is not None and nearest_opp_gap > 0:
                val += 10 * nearest_opp_gap
        else:
            # No visible resources: just reduce distance to center
            val += 0.0

        # Slightly avoid stepping adjacent to opponent (reduce contesting risk)
        val -= 0.8 * max(0, 1 - (cheb(nx, ny, ox, oy)))

        if val > best_val:
            best_val = val
            best = (dx, dy, nx, ny)

    return [int(best[0]), int(best[1])]