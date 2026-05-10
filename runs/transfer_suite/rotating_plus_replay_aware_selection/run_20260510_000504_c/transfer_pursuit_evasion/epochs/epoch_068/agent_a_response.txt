def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    self_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or ("purs" in opp_role)
    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def opp_best(myx, myy):
        # Opponent as pursuer: minimize distance to us
        best = 10**9
        for dx, dy in dirs:
            nx, ny = ox + dx, oy + dy
            if not valid(nx, ny):
                continue
            d = dist(nx, ny, myx, myy)
            if d < best:
                best = d
        if best == 10**9:
            return dist(ox, oy, myx, myy)
        return best

    def wall_pen(x, y):
        # Small penalty for being pushed into corners/walls (helps evader; harmless for pursuer)
        return (min(x, w - 1 - x) + min(y, h - 1 - y)) == 0

    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_now = dist(nx, ny, ox, oy)
        d_after = opp_best(nx, ny) if self_evader else d_now  # if evader, opponent likely pursues next
        # Score: if evader maximize survivability (distance after opponent move); else chase (minimize)
        if self_evader:
            val = (d_after * 2 + d_now) - 0.5 * wall_pen(nx, ny)
        else:
            # pursuer: minimize distance now and discourage risky stalemates near obstacles
            d_next = d_now
            val = -(d_next * 2 - 0.2 * wall_pen(nx, ny))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]