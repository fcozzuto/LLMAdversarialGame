def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    obstacles = observation.get("obstacles", []) or []
    obs = []
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.append((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = []
    pref = (int(observation.get("turn_index", 0)) % 2)
    if pref == 0:
        deltas = [(1, 1), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (-1, -1), (0, 0)]
    else:
        deltas = [(-1, -1), (-1, 0), (0, -1), (1, -1), (1, 0), (0, 1), (-1, 1), (1, 1), (0, 0)]

    def obstacle_penalty(x, y):
        if not obs:
            return 0
        best = 10**9
        for ax, ay in obs:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        if best == 0:
            return -10**7
        if best == 1:
            return -120
        if best == 2:
            return -35
        return 0

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = (0, 0)
    best_score = -10**18 if is_evader else 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        d_now = dist(sx, sy, ox, oy)
        d_next = dist(nx, ny, ox, oy)
        o_next = dist(ox, oy, nx, ny)

        if is_evader:
            # Flee: maximize distance to pursuer; also avoid blocking near obstacles
            score = (d_next * 1000) - (o_next * 2) + obstacle_penalty(nx, ny)
            # Mildly prefer reducing opponent's ability by moving around obstacles
            score += (-d_now + d_next) * 5
            better = score > best_score
        else:
            # Pursue: minimize distance to evader; prioritize moves that "lock in" tighter distance
            score = (d_next * 1000) + (-o_next) + (-obstacle_penalty(nx, ny))
            score = -score  # convert to "maximize"
            better = score > best_score

        if better or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]