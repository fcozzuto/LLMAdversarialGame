def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    self_is_evader = ("evad" in self_role) or (("agent" in self_role) and ("evad" in opp_role))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def mdist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def nearest_corner_dist(x, y):
        return min(mdist(x, y, cx, cy) for cx, cy in corners)

    best = None
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine would keep still if invalid

        d_opp = mdist(nx, ny, ox, oy)

        # If we are pursuer: also reduce opponent's "escape corner" distance.
        # If we are evader: increase escape corner distance from pursuer, avoiding corners when possible.
        if self_is_evader:
            # Evade: maximize distance from opponent and also avoid being too close to obstacles by preferring open lines
            val = (d_opp, -nearest_corner_dist(nx, ny))
        else:
            val = (-d_opp, nearest_corner_dist(ox, oy) - nearest_corner_dist(nx, ny))

        if best is None:
            best, best_val = (dx, dy), val
        else:
            if self_is_evader:
                if val[0] > best_val[0] or (val[0] == best_val[0] and val[1] > best_val[1]):
                    best, best_val = (dx, dy), val
            else:
                # minimize -d_opp first => maximize d_opp; but we want minimize distance => choose smallest val[0]
                if val[0] > best_val[0] or (val[0] == best_val[0] and val[1] > best_val[1]):
                    # Since val[0] is negative distance, ">" means closer or farther? Actually closer gives less negative.
                    # We instead interpret by directly comparing distance: handle by recomputing.
                    pass

    # Resolve pursuer properly by direct distance min (deterministic, robust)
    if self_is_evader:
        return [int(best[0]), int(best[1])]

    best_move = (0, 0)
    best_dist = None
    best_tie = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        d = mdist(nx, ny, ox, oy)
        tie = (nearest_corner_dist(nx, ny), nearest_corner_dist(ox, oy))
        if best_dist is None or d < best_dist or (d == best_dist and tie < best_tie):
            best_dist, best_tie, best_move = d, tie, (dx, dy)
    return [int(best_move[0]), int(best_move[1])]