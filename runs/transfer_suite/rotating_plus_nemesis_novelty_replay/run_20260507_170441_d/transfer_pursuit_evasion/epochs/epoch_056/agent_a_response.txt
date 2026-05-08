def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)
    if ("pursuer" in opp_role) and ("evader" in self_role):
        pursuer = False

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_move(want_reduce):
        # want_reduce: True => minimize distance; False => maximize
        cx = ox - sx
        cy = oy - sy
        sgnx = 0 if cx == 0 else (1 if cx > 0 else -1)
        sgny = 0 if cy == 0 else (1 if cy > 0 else -1)
        # Prefer direct (possibly diagonal), then fallbacks
        preferred = [(sgnx, sgny), (sgnx, 0), (0, sgny), (0, 0)]
        tried = set()
        cand = []
        for dx, dy in preferred:
            if (dx, dy) in tried:
                continue
            tried.add((dx, dy))
            if free(sx + dx, sy + dy):
                cand.append((dx, dy))
        for dx, dy in dirs:
            if (dx, dy) in tried:
                continue
            tried.add((dx, dy))
            if free(sx + dx, sy + dy):
                cand.append((dx, dy))
        def cheb(x1, y1, x2, y2):
            ax, ay = abs(x1 - x2), abs(y1 - y2)
            return ax if ax > ay else ay
        best = None
        best_score = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, ox, oy)
            score = d if want_reduce else -d
            # tie-breaker: fewer changes; then lexicographic on (dx,dy)
            tieb = (abs(dx) + abs(dy), dx, dy)
            if best is None or score > best_score or (score == best_score and tieb < best_tieb):
                best = (dx, dy)
                best_score = score
                best_tieb = tieb
        return list(best)

    if pursuer:
        return best_move(True)
    else:
        # Evader: move to increase distance while staying collision-free
        return best_move(False)