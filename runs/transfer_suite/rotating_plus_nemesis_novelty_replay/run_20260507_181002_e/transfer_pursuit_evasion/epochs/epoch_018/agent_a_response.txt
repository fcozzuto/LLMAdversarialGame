def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    my_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            my_moves.append((nx, ny, dx, dy))
    if not my_moves:
        return [0, 0]

    srole = str(observation.get("self_role", "")).lower()
    orole = str(observation.get("opponent_role", "")).lower()

    i_am_pursuer = ("pursuer" in srole) or ("chaser" in srole) or ("catch" in srole) or ("pursuit" in srole)
    if "evader" in srole or "evad" in srole:
        i_am_pursuer = False
    if ("pursuer" in orole) or ("chaser" in orole) or ("catch" in orole) or ("pursuit" in orole):
        i_am_pursuer = False

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    opp_moves = []
    for dx, dy in dirs:
        nx, ny = ox + dx, oy + dy
        if free(nx, ny):
            opp_moves.append((nx, ny))

    # If we are pursuer: assume opponent tries to maximize distance; we choose move minimizing resulting distance.
    # If we are evader: assume opponent tries to minimize distance; we choose move maximizing resulting distance.
    best = None
    best_val = None
    for nx, ny, dx, dy in my_moves:
        if not opp_moves:
            val = -dist2(nx, ny, ox, oy) if i_am_pursuer else dist2(nx, ny, ox, oy)
        else:
            if i_am_pursuer:
                # opponent picks move maximizing our distance
                max_d = -10**18
                for ax, ay in opp_moves:
                    d = dist2(nx, ny, ax, ay)
                    if d > max_d:
                        max_d = d
                val = -max_d
            else:
                # opponent picks move minimizing our distance (most dangerous)
                min_d = 10**18
                for ax, ay in opp_moves:
                    d = dist2(nx, ny, ax, ay)
                    if d < min_d:
                        min_d = d
                val = min_d
        # tie-break deterministically: prefer smaller |dx|+|dy|, then stable order by (dx,dy)
        tie = (abs(dx) + abs(dy), dx, dy)
        if best is None or val > best_val if not i_am_pursuer else val > best_val:
            best = (dx, dy, val, tie)
            best_val = val
        else:
            # For pursuer we are minimizing distance => val is negative distance; maximizing val still works.
            if val > best_val:
                best = (dx, dy, val, tie)
                best_val = val
            elif val == best_val:
                if tie < best[3]:
                    best = (dx, dy, val, tie)
    return [int(best[0]), int(best[1])]