def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evad" in role

    def edge_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    def dist2(x, y, x2, y2):
        dx = x - x2
        dy = y - y2
        return dx * dx + dy * dy

    def obs_min_dist(x, y):
        if not obstacles:
            return 8.0
        best = 999999
        for (px, py) in obstacles:
            d = dist2(x, y, px, py)
            if d < best:
                best = d
        return best ** 0.5

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d = dist2(nx, ny, ox, oy)
        ed = edge_dist(nx, ny)
        od = obs_min_dist(nx, ny)

        # Encourage strong pursuit/evasion while steering away from obstacles.
        if is_evader:
            # Wall-run bias: prefer being closer to an edge.
            score = d + 0.6 * (8 - ed) + 0.15 * od
        else:
            score = -d + 0.10 * (8 - ed) + 0.10 * od

        if best_score is None:
            best_score = score
            best_move = [dx, dy]
        else:
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]