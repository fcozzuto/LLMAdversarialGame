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
    is_pursuer = any(k in self_role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    pref = [4, 1, 3, 5, 7, 0, 2, 6, 8]  # deterministic tie-break (center first, then cardinal, then diag)
    dirs_pref = []
    for i in pref:
        dirs_pref.append(i)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        ax = abs(x1 - x2)
        ay = abs(y1 - y2)
        return ax if ax > ay else ay

    def nearest_obs_dist(x, y):
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

    best_score = None
    best_move = (0, 0)

    for idx in dirs_pref:
        dx, dy = moves[idx]
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        dist = cheb(nx, ny, ox, oy)
        obs_d = nearest_obs_dist(nx, ny)

        # Encourage pursuer to reduce distance; evader to increase it.
        if is_pursuer:
            # primary: minimize dist; secondary: maximize clearance from obstacles
            score = -dist * 1000 + obs_d
        else:
            # primary: maximize dist; secondary: maximize clearance from obstacles
            score = dist * 1000 + obs_d * 2

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]