def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("pursuer" in role) or ("hunter" in role) or ("chaser" in role) or ("tagger" in role) or ("capture" in role) or True
    if "evader" in role or "runner" in role:
        pursuer = False

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    # Heuristic: if pursuing, aggressively reduce distance; if evading, maximize distance.
    # Also lightly penalize positions that are "adjacent" to obstacles to avoid getting stuck by zigzags.
    def obstacle_adjacency(x, y):
        cnt = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    cnt += 1
        return cnt

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy

        # Capture radius is 0; still, prioritize exact contact if it happens.
        dist = abs(nx - ox) + abs(ny - oy)
        cheb = max(abs(nx - ox), abs(ny - oy))
        obs_pen = obstacle_adjacency(nx, ny)
        # Encourage staying mobile: prefer non-zero moves slightly when distances tie.
        move_pen = 0 if (dx == 0 and dy == 0) else -0.01

        if pursuer:
            val = (dist * 1000) + (cheb * 10) + (obs_pen * 3) + move_pen
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]
        else:
            val = (-dist * 1000) + (-cheb * 10) + (obs_pen * 3) - move_pen
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]