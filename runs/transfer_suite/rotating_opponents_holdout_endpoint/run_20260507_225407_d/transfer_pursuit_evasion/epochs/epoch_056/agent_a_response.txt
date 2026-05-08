def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_evader_role(role):
        r = (role or "").lower()
        return ("evader" in r) or ("evasion" in r) or ("avoid" in r)

    self_evader = is_evader_role(observation.get("self_role", ""))
    opp_evader = is_evader_role(observation.get("opponent_role", ""))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def best_response(px, py, ex, ey, response_evader):
        # response_evader=True => maximize distance, else minimize
        best = None
        best_score = None
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not inb(nx, ny):
                continue
            d = dist2(nx, ny, ex, ey)
            score = d if response_evader else -d
            if best is None or score > best_score or (score == best_score and (nx, ny) < best):
                best = (nx, ny)
                best_score = score
        return best if best is not None else (px, py)

    # 2-ply: choose our move, then opponent greedy response by their role
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        rox, roy = best_response(ox, oy, nx, ny, opp_evader)
        d = dist2(nx, ny, rox, roy)
        val = d if self_evader else -d
        # Encourage moving away from walls when evading; discourage when pursuing to open lanes
        if self_evader:
            edge_bias = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
            val += edge_bias * 0.01
        else:
            edge_bias = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
            val -= edge_bias * 0.01
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]